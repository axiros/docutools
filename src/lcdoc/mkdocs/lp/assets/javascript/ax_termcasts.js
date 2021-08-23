/*
# Yet Another TermCast Viewer

The thingy can play .json files as produced from TermCast

The recordings can be flows with timings or shots, without timings - TermCast offers a switch for that (-S)

## Usage
    <termcast
          src="/assets/my_recording.json"
          [outer_scrolls="xy"]
          [inner_scrolls="y"]
          [inner_bgcol="black"]
          [rows="10"]
      />

    <termcast src="/assets/my_recording.json" />


## Requirements

- RxJS, xterm2.js
- Casts in json, like [[<contframe1>, ts1], ...]
- They SHOULD contain a first item indicating meta data, mainly rows cols of recording
- They should not have been resized during recording


## Dev

'Redux' single state architecture combined with RX / cycle.js:
All state kept in 'tag.s.state' (like a redux store)
- pushed through one stream (RX)
- catching ALL user intent (cycle)
- realizing the intent in a stream subscription only, updating screen and state

=> Forbidden to change the state (tag) within the stream, only allowed before
the stream starts (setup) and in its subscription.  In the stream ops
themselves we just contemplate on the user intent and the necesssary screen
updates do to be done in the next cycle.

 */
function setup_termcasts(window, document) {
  var TC = this
  const dbg_stream = false; // show the main stream items
  const dbg_store = false; // show the store for any stream new item
  const stream = Rx.Observable; // matter of personal taste
  const empty$ = stream.empty();
  const tick_duration = 30; // every 30 ms a terminal update with new frames while playing

  log = (x) => {
    console.log(x);
    return x;
  };

  // functions
  er = (el) => (el ? el : document);
  by_tag_name = (name, el) => er(el).getElementsByTagName(name);
  by_id = (id, el) => er(el).getElementById(id);
  by_cls_name = (cls, el) => er(el).getElementsByClassName(cls);
  get_elmt = (cls, el) => by_cls_name(cls, el)[0];
  var all_xterms = () => by_tag_name("xterm");
  var all_xterm_fetchs = () => by_tag_name("xterm_fetch");
  var all_casts = () => by_tag_name("termcast");
  height = (el) => parseInt(window.getComputedStyle(el).height);
  width = (el) => parseInt(window.getComputedStyle(el).width);
  // all clicks on an element
  clicks$ = (name, el) => stream.fromEvent(by_cls_name(name, el), "click");
  attr = (name, el, dflt) => {
    x = er(el).getAttribute(name);
    return x ? x : dflt;
  };

  String.prototype.replace_all = function (search, replacement) {
    var target = this;
    try {
      return target.replace(new RegExp(search, "g"), replacement);
    } catch (err) {
      return target;
    }
  };
  contained = (item, arr) => arr.indexOf(item) > -1;

  const { fromEvent } = Rx.Observable;
  function drag_and_drop(element) {
    /* only exception to the one stream concept.
     * D&D is a standard stream, will put into a lib.
     * Downside: Does not see escape keys
     * */
    const el = element;
    el.is_draggable = true;

    const mousemove = fromEvent(document, "mousemove");

    fromEvent(el, "mousedown")
      .flatMap((md) => {
        let d = md.target;
        while (!d.is_draggable) d = d.parentElement;
        // add window offset only if position of d is relative:
        const style = window.getComputedStyle;
        const startX = md.clientX, // + window.scrollX,
          startY = md.clientY, // + window.scrollY,
          startLeft = parseInt(style(d).left) || 0;
        startTop = parseInt(style(d).top) || 0;
        return mousemove
          .map((mm) => {
            mm.preventDefault();
            return {
              left: startLeft + mm.clientX - startX,
              top: startTop + mm.clientY - startY,
            };
          })
          .takeUntil(fromEvent(document, "mouseup"));
      })
      .subscribe((pos) => {
        el.style.top = pos.top + "px";
        el.style.left = pos.left + "px";
      });
  }

  function tag_html(mode, tag) {
    let help_table = get_help_table();
    switch (mode) {
      case "loading":
        let src = attr("src", tag);
        return `
                    <div><i class="fa fa-cloud-download" />
                        ...loading cast ${src}
                    </div>
                   `;
      case "loaded":
        return `
    <div class="termcast_player" width="100%" style="color: #999">
        <div class="term_controls">
        <i class="term_info fa fa-info-circle"     title ="info"></i>
        <i class="term_play_btn fa fa-play"        title ="play/resume"></i>
        <i class="term_loop fa fa-circle-o-notch"  title ="loop"></i>
        <i class="term_rewind fa fa-fast-backward" title ="rewind"></i>

        <span class="right_float" style="position  : relative;
                                        float      : right;
                                        font-family: monospace" />
            <i class="fa fa-tachometer" title ="playback speed multiplier"></i>
            <span class="term_play_speed">1</span></i>
            <span class="term_timer"></span>
            <i class="term_maxmin fa fa-expand" title ="toggle height"></i>
        </div>
        </div>
        <div class="term_wrap" style="position   :relative;
                                        width    : 100%   ;
                                        overflow : hidden ">

        <terminal />

        <div style="z-index: 2; cursor: pointer; position: absolute; visibility: hidden; top: 3px; left: 10px;"
            class="term_help_insert draggable">
            ${help_table}
        </div>
        <div style="z-index: 3; left: 50%; top: 20%; cursor: pointer; position: absolute; visibility: hidden;"
            class="search_words_insert draggable">
            <table><tr><td>Search Items<br><b>j</b>: Jump to next match,
                <b>&#92;n</b>: search linebreaks. Tip: use prompt to jump through cmds</td></tr>
                <tr><td>
                    <input width="100%" class="search_words has_user_input"></input>
                </td></tr>
            </table>
        </div>

        <i style="color: #777; z-index: 1; position: absolute;"
            class="term_play_btn_big fa fa-5x fa-play"></i>

    </div>
    `;
    }
  }

  function dbg(e) {
    debugger;
    return e;
    //console.log(els.selectionStart)
  }

  /* ------------------------------------------------------------------------- *
   *                      HANDLING USER INTENT (subscr to main stream)
   * ------------------------------------------------------------------------- */
  function reset(tag) {
    tag.s.cur_time = 0;
    tag.s.next_frame_nr = 0;
    tag.s.cast_ended = false;
    tag.s.is_playing = false;
  }

  do_search_terms = (tag, r) => {
    let hilite = r.ev.user_input;
    reset(tag);
    try {
      console.log("regexing", hilite);
      tag.s.hilite = tag.s.jump_str = new RegExp(hilite);
    } catch (err) {
      console.log(err.message);
      tag.s.hilite = "";
    }
  }

  do_update_controls_view = (tag) => {
    /* done instantly at any change, i.e. also within stream */
    // first reset all:
    let speed = get_elmt("term_play_speed", tag);
    speed.innerHTML = "" + 2 ** tag.s.play_speed;
    let bb = get_elmt("term_play_btn_big", tag);
    bb.style.visibility = "hidden";
    let clloop = get_elmt("term_loop", tag).classList;

    clloop.remove("fa-spin");
    let cl = get_elmt("term_play_btn", tag).classList;
    stream
      .from(["fa-pause", "fa-play", "fa-stop-circle-o", "fa-step-forward"])
      .subscribe((x) => cl.remove(x));

    if (tag.s.is_shot) {
      get_elmt("termcast_player", tag).style.visibility = "hidden";
    }

    if (tag.s.cast_ended) cl.add("fa-stop-circle-o");
    else if (tag.s.is_playing) cl.add("fa-pause");
    else if (tag.s.do_one) cl.add("fa-step-forward");
    else if (tag.s.do_one_back) cl.add("fa-step-backward");
    else {
      cl.add("fa-play");
      bb.style.visibility = "visible";
    }

    tag.s.is_playing && tag.s.looping ? clloop.add("fa-spin") : 0;
    return tag;
  }



  function show_hide(tag, cls) {
    let el = get_elmt(cls, tag);
    let before = el.style.visibility;
    el.style.visibility = before == "hidden" ? "visible" : "hidden";
    if (before == "visible") tag.term.focus();
    // focus on first element with user input - if any:
    else
      stream
        .from([get_elmt("has_user_input", el)])
        .take(1)
        .filter((it) => it)
        .subscribe((it) => it.focus());
    return before == "hidden";
  }

  do_quit_play = (tag)     => tag.s.is_playing = false
  do_scroll_top = (tag)    => tag.term.scrollToTop();
  do_toggle_info = (tag)   => show_hide(tag, "term_help_insert");
  do_toggle_search = (tag) => show_hide(tag, "search_words_insert");
  do_escape = (tag) => {
    stream
      .from(by_cls_name("draggable", tag))
      .subscribe((el) => (el.style.visibility = "hidden"));
    tag.term.textarea.focus();
  }
  do_toggle_maxmin = (tag) => {
    tag.s.fullscreen = !tag.s.fullscreen;
    let tw = get_elmt("term_wrap", tag);
    let cl = get_elmt("term_maxmin", tag).classList;
    let trr = tag.s.recorder_rows;
    cl.remove("fa-expand");
    cl.remove("fa-compress");

    if (tag.s.fullscreen) {
      cl.add("fa-compress");
      tag.s.old_geo = tag.term.geometry;
      if (trr && trr != tag.s.old_geo[1]) {
        tag.term.resize(tag.s.recorder_cols, trr);
      } else {
        // use what we have
        let H = height(by_tag_name("body")[0]);
        let W = width(by_tag_name("body")[0]);
        let cm = tag.term.charMeasure;
        tag.term.resize(parseInt(W / cm.width), parseInt(H / cm.height));
      }
      if (!tag.s.is_playing) tag.s.is_playing = true;
    } else {
      cl.add("fa-expand");
      tag.term.resize(tag.s.old_geo[0], tag.s.old_geo[1]);
    }
  }

  do_toggle_speed = (tag, r) => {
    let cs = tag.s.play_speed;
    tag.s.play_speed = r.ev.key == "s" ? cs - 1 : r.ev.key == "d" ? 0 : cs + 1;
  }

  do_toggle_loop = (tag) => {
    /* the loop button also starts but does not stop the cast */
    // if playing, keep playing, else start
    tag.s.looping = !tag.s.looping; // || ! tag.s.is_playing
    if (!tag.s.is_playing) do_toggle_play(tag);
  }

  do_toggle_play = (tag) => {
    tag.s.is_playing = !tag.s.is_playing;
    if (tag.s.cast_ended) {
      reset(tag);
      tag.s.is_playing = true;
    }
  }


  do_toggle_rewind = (tag) => {
    reset(tag);
    tag.s.is_playing = true;
  }

  do_one = (tag, r) => {
    // realized in push_framesets
    tag.s.do_one = 1;
    tag.s.is_playing = false;
  }

  do_one_back = (tag, r) => {
    tag.s.jump_frame = Math.max(tag.s.next_frame_nr - 1, 0);
    reset(tag);
  }

  do_jump = (tag, r) => {
    tag.s.jump_str = tag.s.last_jump;
  }



  do_scroll_bottom = (tag) => {
    tag.term.scrollToBottom();
  }

  function dispatch_intent_function(r) {
    // r.side_effect e.g. "do_scroll_top" - we call the do_scoll_up function here
    if (!r.side_effect) return;
    TC[r.side_effect](r.tag, r);
  }

  function add_intent_function(r) {
    if (r.frames) return r;
    if (r.ev.key != "c") r.ev.preventDefault();
    let func, funcs, inp;
    if (contained(r.ev.type, ["keyup", "keydown"])) {
      r["ev_type"] = "key";
      inp = r.ev.user_input;
      if (inp && inp.length > 0) func = "do_search_terms";
      else if (r.ev.key == "Escape") func = "do_escape";
      else {
        log("intent key: " + r.ev.key);
        stream
          .from([
            ["sdf", "do_toggle_speed"],
            ["p ", "do_toggle_play"],
            ["q ", "do_quit_play"],
            ["r ", "do_toggle_rewind"],
            ["i ", "do_toggle_info"],
            ["l", "do_toggle_loop"],
            ["j", "do_jump"],
            ["o", "do_one"],
            ["O", "do_one_back"],
            ["t", "do_scroll_top"],
            ["b", "do_scroll_bottom"],
            ["m", "do_toggle_maxmin"],
            ["/", "do_toggle_search"],
          ])
          .filter((k) => k[0].indexOf(r.ev.key) > -1)
          .subscribe((k) => (func = k[1]));
      }
    } else if (r.ev.type == "click") {
      // no preventDefault, we want copy and paste !
      r["ev_type"] = "click";
      let tag = r.tag,
        ev = r.ev,
        el = r.ev.target;
      while (el) {
        cl = el.classList;
        cl.contains("term_play_btn")
          ? (func = "do_toggle_play")
          : cl.contains("term_play_btn_big")
          ? (func = "do_toggle_play")
          : cl.contains("term_loop")
          ? (func = "do_toggle_loop")
          : cl.contains("term_rewind")
          ? (func = "do_toggle_rewind")
          : cl.contains("term_info")
          ? (func = "do_toggle_info")
          : cl.contains("term_maxmin")
          ? (func = "do_toggle_maxmin")
          : false;

        if (el == tag || func) break;
        el = el.parentElement;
      }
    }
    // thats the function realizing the intent:
    r.side_effect = func;
    log("user intent function: " + func);
    return r;
  }

  function reduce_user_input(ev) {
    // when its open we need to reduce everything entered
    // i.e. emit a stream of current text
    // plus we restrict the speed:
    return ((ev) => {
      ev.user_input = ev.target.value;
      return ev;
    }).filter((ev) => ev.user_input.length > 0);
    /* If its a textarea:
        // we remove duplicate lines and also not add lines with < 4 chars:
        .map(ev => {
            let lines = ev.target.value.replace(/\r\n/g,"\n").split("\n")
            let v = []
            stream.from(lines)
                .filter(line => line.length > 3)
                .distinct() // fockin_luvin_it
                .subscribe(line => v.push(line))
            ev.user_input = v
            return ev })
            */
  }

  /* ------------------------------------------------------------------------- *
   *                      VIDEO STREAM CREATION                                *
   * ------------------------------------------------------------------------- */
  function push_framesets(observer, tag) {
    /* nexting a bunch of frames if tag is playing.
     * No state set here, could be parallel to user intent
     * Actually not anymore, since we subscribe now to a combinattion of user
     * events and the framesets produced here => no collission possible.
     * But still its cleaner to not change the state here but in the subs only
     * */
    let data = tag.recording_data,
      frames,
      frame,
      frame_nr,
      match;
    stream
      .interval(tick_duration)
      .filter(
        (tick) =>
          tag.s.is_playing ||
          tag.s.do_one ||
          tag.s.jump_str ||
          tag.s.jump_frame != false
      )
      .map((tick) => {
        /* push all frames until tag.s.cur_time + tick_duration */
        let frame_nr = tag.s.next_frame_nr;
        if (frame_nr == 0) tag.term.reset();
        let to_time = tag.s.cur_time + tick_duration * 2 ** tag.s.play_speed;
        frames = [];

        add = (frame, frames) => {
          frames.push(frame);
          return 1;
        };

        while (frame_nr < data.length) {
          s = ""; // total content string to search within
          frame = data[frame_nr];

          if (tag.s.do_one) {
            frame_nr += add(frame, frames);
            break;
          } else if (tag.s.jump_frame) {
            frame_nr += add(frame, frames);
            if (tag.s.jump_frame <= frame_nr) {
              break;
            }
          } else if (tag.s.jump_str) {
            frame_nr += add(frame, frames);
            s = frame[0].length > 20 ? frame[0] : s + frame[0];
            if (s.match(tag.s.jump_str)) {
              // adding all frames to the next linebreak.
              // to not stop at exactly at the match:
              while (frame_nr < data.length && frame[0].indexOf("\n") == -1) {
                frame = data[frame_nr];
                frame_nr += add(frame, frames);
              }
              break;
            }
          } else {
            // normal playing
            if (frame[1] >= tag.s.cur_time) break;
            frame_nr += add(frame, frames);
          }
        }
        observer.next({ tag: tag, frames: frames });
      })
      .subscribe((item) => 0);
  }

  /* ------------------------------------------------------------------------- *
   *                      VIDEO STREAM PLAYBACK (subscr. to main stream)       *
   * ------------------------------------------------------------------------- */
  function hilite_content(res) {
    let esc = String.fromCharCode(27);
    let color = esc + "[48;5;126m";
    let hilite = res.tag.s.jump_str || res.tag.s.hilite;
    if (!hilite) return res;
    let match = res.out.match(hilite);
    if (!match) return res;
    res.out = res.out.replace_all(match, color + match + esc + "[0m");
    return res;
  }

  function update_timer(r, tag) {
    let d = new Date(tag.s.cur_time).toUTCString().substr(17, 8);
    let n = tag.s.next_frame_nr,
      a = tag.recording_data.length;
    tag.sh_play_time.innerHTML = `<font size="-2">${n}/${a}</font> ${d}`;
  }

  do_play_frames = (r) => {
    /* writing the ansi frames to xterm2.js
     * the frames could be the result of a jump, one, ... operation, i.e. where
     * the player is not actually running
     * reminder: frames is an array of [content, timestamp] tuples
     * */
    //term.debug = true
    let tag = r.tag;
    stream
      .from(r.frames)
      .reduce((out, frame) => out + frame[0], "")
      .map((out) => {
        return { tag: tag, out: out };
      })
      .map(hilite_content)
      .subscribe((res) => {
        tag.term.write(res.out);
        //tag.term.writeln('')
        // aaargh, the write is so async...
        //if (  tag.s.is_shot ) {
        //    tag.term.scrollDisp(1000)
        //    tag.term.scrollDisp(-5)
        //$('.term_wrap').trigger({type: 'keypress', which: 't'.codePointAt(0)})
      });
    tag.s.next_frame_nr += r.frames.length;
    update_timer(r, tag);
    let ts_old = tag.s.cur_time;
    tag.s.cur_time = tag.s.is_playing
      ? ts_old + tick_duration * 2 ** tag.s.play_speed
      : r.frames[r.frames.length - 1][1]; // do_one, jump, search
    tag.s.do_one = false;

    if (tag.s.next_frame_nr >= tag.recording_data.length) {
      reset(tag);
      tag.s.looping ? (tag.s.is_playing = true) : (tag.s.cast_ended = true);
    }
    if (tag.s.showing_preview) {
      reset(tag);
      tag.s.showing_preview = false;
    }
    tag.s.jump_frame = false;
    if (tag.s.jump_str) {
      tag.s.last_jump = tag.s.jump_str;
      tag.s.jump_str = false;
    }
  }

  /* ------------------------------------------------------------------------- *
   *                      DOM STREAM TAG CREATION
   * ------------------------------------------------------------------------- */
  function set_scrolls(tag, attr_name, to_tag) {
    to_tag.style.overflow = "hidden";
    let os = attr(attr_name, tag, "");
    let i = os.length;
    while (i--) to_tag.style["overflow-" + os.charAt(i)] = "scroll";
  }

  function setup_loaded(tag, shotmode) {
    /* setting up the terminal tag after page load.  The tag itself is our
     * global store for state which we may only change before the event stream
     * and in its subscription */
    tag.term = new Terminal();
    tag.innerHTML = tag_html("loaded", tag);

    let term_el = by_tag_name("terminal", tag)[0];
    let term_wrap = get_elmt("term_wrap", tag);
    set_scrolls(tag, "outer_scrolls", term_wrap);

    let rows = 20,
      cols = 80;
    let rec = tag.recording_data;
    tag.term.open(term_el, (focus = true));
    //
    //   tag.term.insertMode = true
    //   tag.term.applicationCursor = true
    //   tag.term.applicationKeypad = true
    //   tag.term.cursorBlink = true
    //   tag.term.screenKeys = true
    //   tag.term.userScrolling = true
    //   tag.term.flowControl = true
    //   tag.term.useFlowControl = true

    let drags = by_cls_name("draggable", tag);
    for (i = 0; i < drags.length; i++) drag_and_drop(drags[i]);

    tag.s.recorder_rows = 0; // maybe we have the size not in Termcast data
    // first item of the json is the meta definitions (rows, colors, kb, ...)
    let meta;

    if (rec[0].rows) {
      meta = rec.shift();
      let author = meta.by || "n.a.";
      let kB = meta.kB;
      let ts = meta.ts || "-";
      if (kB) kB = ", ${kB} kB (uncompressed)";
      rows = tag.s.recorder_rows = meta.rows || 20;
      cols = tag.s.recorder_cols = meta.cols || 80;
      get_elmt("term_meta", tag).innerHTML = `<font size="-2">
            ${ts}, ${author}, ${rows}rows x ${cols} columns${kB}</font>`;
    }

    if (rec.length > 1) {
      let x = rec[rec.length - 1][0];
      if (x.endsWith("exit\\r\\n'")) rec.pop();
    }

    rows = parseInt(attr("rows", tag, rows));
    cols = parseInt(attr("cols", tag, cols));
    tag.term.resize(cols, rows);

    // shots have no timing information:
    tag.s.is_shot = false;
    if (Number.isInteger(rec[0][1])) {
      // conversion of all escape chars, better do only once:
      for (i = 0; i < rec.length; i++) rec[i][0] = eval(rec[i][0]);
    } else {
      // screenshot only:
      tag.s.is_shot = true;
      // if we did  video and want a shot later we just change the
      // first frame's timing to a non Integer, so we land here.
      // Then we must convert the first items to shot format w/o timings:
      if (rec[0].length == 2) {
        for (i = 0; i < rec.length; i++) rec[i] = rec[i][0];
      }
      // normal shot format: No timings:
      for (i = 0; i < rec.length; i++) rec[i] = [eval(rec[i]), 1];
      //get_elmt("term_controls", tag).style.visibility = "hidden";
    }

    let big_btn = get_elmt("term_play_btn_big", tag);
    big_btn.style.top = (height(term_wrap) - height(big_btn)) / 2 + "px";
    big_btn.style.left = (width(term_wrap) - width(big_btn)) / 2 + "px";

    reset(tag);
    tag.s.play_speed = parseInt(attr("play_speed", tag, 0)); // 2 ** this

    let hilite = attr("hilite", tag);
    let jump_str = attr("jump_str", tag);
    jump_str = jump_str ? jump_str : hilite;
    tag.s.hilite = hilite ? new RegExp(hilite) : "";
    tag.s.jump_str = jump_str ? new RegExp(jump_str) : "";

    // jump to first occurrance of this. jump != hilitie in general
    let jt = attr("jump_frame", tag);

    init_intent = [];

    if (jt > 0) {
      tag.s.jump_frame = jt;
    } else if (tag.s.is_shot) {
      tag.s.is_playing = true;
      // TODO can't work as init intent, we have then not yet frames on the
      // screen:
      init_intent.push({ tag: tag, side_effect: "do_scroll_top" });
      tag.s.scroll = "top";
      tag.term.scrollDisp(1000);
      // go back (exits)
      tag.term.scrollDisp(-5);
    } else {
      tag.s.jump_frame = false;
      if (tag.s.jump_str || tag.s.jump_frame) tag.s.showing_preview = true;
    }

    if (tag.hasAttribute("autoplay")) {
      tag.s.showing_preview = false;
      tag.s.is_playing = true;
    }
    if (tag.hasAttribute("looping")) {
      tag.s.showing_preview = false;
      tag.s.is_playing = true;
      tag.s.looping = true;
    }

    //style the inner terminal:
    let xt = by_cls_name("xterm-viewport", tag)[0];
    xt.style["background-color"] = attr("inner_bgcol", tag, "black");
    set_scrolls(tag, "inner_scrolls", xt);

    tag.sh_play_time = get_elmt("term_timer", tag);
    tag.term.textarea.focus();
    tag.term.linkifier._linkMatchers = [];

    do_update_controls_view(tag);
    run_main_stream(tag, init_intent);
  }

  function run_main_stream(tag, init_intent) {
    is_text_input = (ev) => ev.target.classList.contains("has_user_input");
    key_up$ = stream.fromEvent(tag, "keyup");
    esc$ = key_up$.filter((ev) => ev.key == "Escape");
    // Esc has no keydown

    user_text_inp$ = key_up$
      .filter(is_text_input)
      .filter((ev) => ev.key != "/") // opens search
      .filter((ev) => ev.key != "Escape")
      .filter((ev) => ev.key != "Meta")
      .map((ev) => {
        ev.user_input = ev.target.value;
        return ev;
      })
      // 0 -> we search every character:
      .filter((ev) => ev.user_input.length > 0);

    user_ctrl_key$ = stream
      .fromEvent(tag, "keydown")
      .filter((ev) => ev.key != "Meta")
      .filter((ev) => !is_text_input(ev));

    user_intent$ = stream
      .fromEvent(tag, "click")
      .merge(user_text_inp$)
      .merge(user_ctrl_key$)
      .merge(esc$)
      .map((ev) => {
        return { tag: tag, ev: ev };
      })
      .map(add_intent_function);

    stream
      .create((o) => push_framesets(o, tag))
      .merge(stream.from(init_intent))
      .merge(user_intent$)
      .map((item) => (dbg_stream ? log(item) : item))
      .map((item) => {
        if (dbg_store) log(JSON.stringify(item.tag.s, null));
        return item;
      })
      .subscribe((r) => {
        r.frames
          ? do_play_frames(r) // paint a bunch of frames
          : dispatch_intent_function(r); // realize user intent

        if (r.ev || r.tag.s.cast_ended) do_update_controls_view(tag);
      });
  }

  function fetch_term_raw(url, callback) {
    fetch(url)
      .then((response) => response.text())
      .then((data) => callback(null, data))
      .catch((error) => callback(error, null));
  }
  function fetch_term_json(url, callback) {
    fetch(url)
      .then((response) => response.json())
      .then((json) => callback(null, json))
      .catch((error) => callback(error, null));
  }

  // ---------------------------------------------------------------------assets:
  get_help_table = () => {
    let ht = `
    <table style="font-size: 10px">
        <tr><td colspan="4"><span class="term_meta"></span></td></tr>

        <tr><td>!p         </td> <td> Toggle !Play / !Pause                               </td>
            <td>!q         </td> <td> !Quit Play                                          </td></tr>
        <tr><td>!l         </td> <td> Toggle !Looping Playback                            </td>
            <td>!s, !d, !f </td> <td> !Slower / !Default / !Faster Playback Speed         </td></tr>
        <tr><td>!m         </td> <td> Toggle !Maximize / !Minimize. Starts if not running </td>
            <td>!r         </td> <td> !Rewind                                             </td></tr>
        <tr><td>!o/(!O)    </td> <td> !One frame (back) at a time                         </td>
            <td>!t/!b      </td> <td> Scroll to !Top or !Bottom                           </td></tr>
        <tr><td>!i         </td> <td> Toggle This !Info                                   </td>
            <td>!/         </td> <td> Search substring                                    </td></tr>
        <tr><td>!j         </td> <td> !Jump to next occurrance of search word             </td>
            <td>!ESC       </td> <td> Close all popups                                    </td></tr>

    </table>`;
    // 'foo !abar' => 'foo <b>a</b>bar'
    let s = "";
    stream
      .from(ht.split("!"))
      .map((part, i) => {
        if (i == 0) return part;
        return "<b>" + part[0] + "</b>" + part.substring(1);
      })
      .subscribe((i) => (s += i));
    return s;
  };

  function setup_tag(tag) {
    /* add the player icons, register an observable data stream */
    console.log("setting up", tag);
    tag.s = {}; // the global state, like a redux store
    let src = attr("content", tag);
    if (!src) src = tag.innerHTML.trim();
    if (!src) src = tag.recording_data;
    if (src) {
      tag.recording_data = src;
      setup_loaded(tag, true);
    } else {
      tag.innerHTML = tag_html("loading", tag);
      let src = attr("src", tag);
      function run_json(err, json) {
        if (err) {
          console.log(err);
          return;
        }
        tag.recording_data = json;
        setup_loaded(tag);
      }
      fetch_term_json(src, run_json);
    }
    return tag;
  }

  function render_xterm(tag) {

    let p = tag.parentNode // parent div
    let pre = p.nextElementSibling // container of raw ansi
    let code = by_tag_name('code', pre)[0]
    if (code.innerText.trim() == 'remote_content') {
        // we attached in img element to it:
        let url = pre.nextElementSibling.firstElementChild.href
        function cb(err, resp) {
            code.innerHTML = resp
            return window.TermCast.render_xterm(tag)
        }
        return fetch_term_raw(url, cb)
    }

    let bg = getComputedStyle(pre).getPropertyValue('--md-code-bg-color')
    var term = new Terminal({cursorStyle: 'bar', cursorWidth: 1,
        theme: {background:  bg, cursor: bg}})

      //TODO: clipboard btn support
    //by_cls_name("md-clipboard", pre)[0].addEventListener('click', foo)
    //by_cls_name("md-clipboard", pre)[0].setAttribute('data-clipboard-text', '#foo')
    //let fit = new FitAddon.FitAddon()
      //
    //TODO: search support
    //let search = new SearchAddon.SearchAddon()

    //term.loadAddon(fit)
    //term.loadAddon(search)
    //term.setOption('fontSize', 9)
    term.setOption('rendererType', 'dom')
    term.setOption('disableStdin', true)
    //term.setOption('scrollback', 0)


    var lines = code.innerText
    lines = lines.split('\n')

    code.innerText = ''
    term.open(code)
    //try {fit.fit()
    //} catch(e) {console.log(e); debugger;}
    //term.element.style['margin-left'] = '-2em' // todo cope with scrollbar
    if (tag.getAttribute('root') != null) pre.style['border-left'] = '2px solid magenta'

    term.writeln(''); for (var i=0; i<lines.length-1; i++) term.writeln(lines[i])
    term.write('\x1b[F') //cursor up saves a line

    term.resize(200, lines.length+1)
    by_cls_name('xterm-viewport', term.element)[0].style['overflow'] = 'hidden'
    let set_dbg = () => { window.axcode = code; window.axsearch = search; window.axtag = tag; window.axterm = term; window.axp = p; window.axpre = pre; }
    set_dbg()
    const onIntersection = ([{isIntersecting, target}]) => {

        // We have to hook in and make it visible when inside a tab whcih is clicked, since:
        // the new xterm does not render when not visible, but does not see the tab clicks.
        if (isIntersecting && !term.is_rendered) {
            var l = lines.length
            term.resize(199, l+1)
            term.is_rendered = true
        }
    }
    const io = new IntersectionObserver(onIntersection, {threshold: 1})
    const cont = tag.parentNode.parentNode
    io.observe(cont)
  }
  window.TermCast = {
      stream: stream,
      setup_tag: setup_tag,
      all_casts: all_casts,
      all_xterms: all_xterms,
      all_xterm_fetchs: all_xterm_fetchs,
      render_xterm: render_xterm,
  };
}

setup_termcasts(window, document);
var TC = window.TermCast;

window.addEventListener("load", function () {
  TC.stream.from(TC.all_xterm_fetchs()).subscribe(TC.render_xterm);
  TC.stream.from(TC.all_xterms()).subscribe(TC.render_xterm);
  TC.stream.from(TC.all_casts()).subscribe(TC.setup_tag);
});



