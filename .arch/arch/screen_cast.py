#!/usr/bin/env python
"""
Building Screencasts

"""
from plugins import _tools as tools
from devapp.app import app
import os, sys, json


# ------------------------------------------------------------------------------ config


class Flags(tools.BaseFlags):
    autoshort = ''

    class name:
        """In the recorder application you must manually save with that filename, except for
        - simplescreenrecorder 
        where we can preset it for you.
        """

        n = 'Name of recording. Variable "video_file" (filename of recording) will be derived from it. If not given or not present / discard_video_file_if_present set, we start recorder.'
        d = 'screencast'

    class record_with_timestamp:
        d = False

    class doc_file_name:
        n = 'Filename to derive final storage location and link from'

    class media_folders:
        n = 'Media folders next to org_file to try in the given order. If none is found we will create the first one'
        d = 'screencasts, media, assets, images'

    class discard_video_file_if_present:
        s = 'd'
        d = False

    class video_recorder:
        n = 'Screenrecorder command. Must produce "video_file" for further processing'
        d = 'simplescreenrecorder'

    class thumbnail_creator:
        n = 'How to create the thumbnail. Has no effect when gifs are created'
        d = 'ffmpegthumbnailer -s 300 -i "%(video_file)s" -o "%(thumb_file)s" -t0 -f'

    class link_format:
        n = 'We will print this on stdout. When gifs are created then "gif_link_format" is used instead of this'
        d = '\n\t#+CAPTION: Click to play screencast\n\t[[file:%(cast_rel_path)s][file:%(thumb_rel_path)s]] '

    class post_conf_cmd:
        n = 'After conversion run this'
        d = 'echo " %(link)s " | xclip -i -selection clipboard'

    if 1:

        class to_gif_conversion:
            n = 'Create an animated gif instead of mp4'
            d = False

        class gif_link_format:
            n = 'We will print this on stdout'
            d = ' [[file:%(cast_rel_path)s][%(video_file)s]] '

        class ffmpeg_scale:
            n = 'Determines gif quality. 320 lousy, 640: medium, 1280: high quality'
            d = 640

        class ffmpeg_frames_per_second:
            n = 'Determines gif quality'
            d = 10

        class to_gif_converter:
            """
            ffmpeg converter params:
            -ss 30: skip first 30 secs.
            -t 3: stop after 3 seconds of video
            """

            n = 'Converts the recording to animated gif. If not given we link the mp4.'
            d = 'ffmpeg -y -i "%(video_file)s" -filter_complex "fps=%(ffmpeg_frames_per_second)s,scale=%(ffmpeg_scale)s:-1:flags=lanczos[x];[x]split[x1][x2]; [x1]palettegen[p];[x2][p]paletteuse" %(gif_file)s'

        class gif_file:
            n = 'Filename of animated gif'
            d = '%(video_file)s.gif'


main = lambda: tools.main(run, Flags)
FLG = tools.FLG
D = tools.D
exists = tools.exists
do = tools.do
system = tools.system
dirname = os.path.dirname
# ----------------------------------------------------------------------------- actions
class recorders:
    def select():
        r = FLG.video_recorder
        hlp = os.popen(r + ' -h 2>&1').read() or os.popen(r + ' --help 2>&1').read()
        if 'simplescreenrecorder' in hlp:
            return recorders.simplescreenrecorder
        app.die('Unsupported recorder', cmd=r)

    class simplescreenrecorder:
        def set_video_file_dest_and_ts():
            fn_cfg = os.environ['HOME'] + '/.ssr/settings.conf'
            if not exists(fn_cfg):
                app.warn('No settings file - cannot set video_file for you', fn=fn_cfg)
                return
            with open(fn_cfg) as fd:
                s = fd.read()
                F = '\nfile='
                if F in s:
                    s = s.split(F, 1)
                    s = s[0] + F + S.video_file + '\n' + s[1].split('\n', 1)[1]
                F = '\nadd_timestamp='
                if F in s:
                    s = s.split(F, 1)
                    tf = 'true' if FLG.record_with_timestamp else 'false'
                    s = s[0] + F + tf + '\n' + s[1].split('\n', 1)[1]
                FT = '/tmp/rec_settings.conf'
                with open(FT, 'w') as fd:
                    fd.write(s)
                app.info('Have augmented your settings file', fn=FT)
                return FLG.video_recorder + ' --settingsfile="%s"' % FT

        def find_recording():
            # may have timestamp
            fn = S.video_file.rsplit('.', 1)[0]
            d = dirname(fn)
            for f in os.listdir(d):
                ff = d + '/' + f
                if ff.startswith(fn):
                    return ff


def set_full_video_file_name():
    video_file = FLG.name
    if not video_file.startswith('/'):
        video_file = '/tmp/casts/' + video_file
    video_file = os.path.abspath(video_file)
    if not video_file.endswith('.mp4'):
        video_file += '.mp4'
    os.makedirs(dirname(video_file), exist_ok=True)
    app.info('recording to', video_file=video_file)
    FLG.name = os.path.basename(video_file).split('.mp4')[0]
    return video_file


def run_screencast_prog():
    rec = recorders.select()
    cmd = rec.set_video_file_dest_and_ts()
    if not cmd:
        app.notify('Expected Filename', video_file=S.video_file)
    do(system, cmd)
    return rec.find_recording()


def to_gif_conversion():
    gf, vf = FLG.gif_file, S.video_file
    gf = gf % state()
    if not gf.startswith('/'):
        gf = dirname(vf) + '/' + gf
        os.makedirs(dirname(gf), exist_ok=True)
    S.gif_file = gf
    cmd = FLG.to_gif_converter % state()
    app.info('Starting conversion', cmd=cmd)
    do(system, cmd)


def create_thumbnail():
    S.thumb_file = S.video_file + '.png'
    cmd = FLG.thumbnail_creator % state()
    app.info('creating thumbnail', cmd=cmd)
    do(system, cmd)


def move_to_dest():
    d = S.doc_file_dir = dirname(os.path.abspath(FLG.doc_file_name))
    if not exists(d):
        app.die('directory of orgfile no found', dir=d)
    mf = [s.strip() for s in FLG.media_folders.split(',')]
    for m in mf:
        dt = d + '/' + m
        if exists(dt):
            break
    if not exists(dt):
        dt = d + '/' + mf[0]
        app.warn('No media folder found', created=dt, checked=mf)
        os.makedirs(dt)
    S.fn_dest = dt + '/' + os.path.basename(S.fn_cast)
    do(system, '/usr/bin/mv -f "%s" "%s"' % (S.fn_cast, S.fn_dest))
    if not FLG.to_gif_conversion:
        do(system, '/usr/bin/mv -f "%s.png" "%s.png"' % (S.fn_cast, S.fn_dest))


def build_link():
    d = S.fn_dest.split(S.doc_file_dir, 1)
    nfos = {
        'cast_rel_path': '.' + d[1],
        'video_file': S.video_file,
        'name': FLG.name,
    }
    nfos['thumb_rel_path'] = nfos['cast_rel_path'] + '.png'
    if FLG.to_gif_conversion:
        nfos['link'] = FLG.gif_link_format % nfos
    else:
        nfos['link'] = FLG.link_format % nfos
    return nfos


def post_conf_cmd(nfos):
    cmd = FLG.post_conf_cmd % nfos
    app.info('Org link to clipboard', cmd=cmd)
    do(system, cmd)


class S:
    'state'


def state():
    d = tools.FlagsDict(FLG)
    for k in dir(S):
        d[k] = getattr(S, k)
    return d


def run():
    # app.notify('Launching Screencast creation', a=sys.argv)
    app.warn('Starting screenrecordr'.upper(), dir=D())
    S.video_file = do(set_full_video_file_name)

    if FLG.discard_video_file_if_present:
        if exists(S.video_file):
            app.warn('discarding old recording', fn=S.video_file)
            os.unlink(S.video_file)

    if not exists(S.video_file):
        S.video_file = do(run_screencast_prog)
    else:
        msg = 'recording already present'
        app.warn(msg, hint='consider flag discard_video_file_if_present')

    if not S.video_file or not exists(S.video_file):
        app.die('video file not found', filename=S.video_file)

    if FLG.to_gif_conversion:
        if FLG.gif_file and FLG.to_gif_converter:
            do(to_gif_conversion)
            S.fn_cast = S.gif_file
        else:
            app.die('to convert to gif we need to_gif_converter and gif_file flags')
    else:
        S.fn_cast = S.video_file
        do(create_thumbnail)

    if not exists(S.fn_cast):
        app.die('screencast file not found', filename=S.fn_cast)

    app.info('Screencast ready', filename=S.fn_cast)
    if not FLG.doc_file_name:
        return app.warn('No link creation requested, doc_file_name is empty')
    else:
        do(move_to_dest)
    m = do(build_link)

    if FLG.post_conf_cmd:
        do(post_conf_cmd, m)
    app.notify('Done', link=m['link'])
    print(m['link'])
