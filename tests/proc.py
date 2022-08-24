import subprocess

input_path = r"C:\games\Twitch\ClipHunter\tmp\yr3fegiy.mp4"
hms = "00:00:02"
s = "00:00:08"
output_path = r"c:\tmp\out.mp4"
args = ['ffmpeg', '-threads', '1', '-y', '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', input_path, '-ss',
        hms, '-to', s, '-c', 'copy', output_path]
print(' '.join(args))
p = subprocess.Popen(
        args)
p.wait()
print(p.returncode)
try:
    subprocess.check_output(args)
except subprocess.CalledProcessError as e:
    print(e.output)