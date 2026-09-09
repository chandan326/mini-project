"""Build the self-contained 60s tutorial offline using Pillow + FFmpeg/Flite.

Run: python scripts/build_tutorial.py
No API calls, credits, stock footage, user photos, or credentials are used.
The illustrations demonstrate the workflow; they are not diagnostic evidence.
"""
import json
import math
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'static' / 'video'
W, H, FPS = 1280, 720, 24
BG, GREEN, INK, MUTED = '#f2f7f1', '#168354', '#163d2b', '#597264'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SCENES = [
    ('Plant care, made simpler', 'A one-minute guide to AgriHealth AI',
     'Meet Agri Health A I. Explore changes in your plants with photo based guidance for farmers and gardeners.',
     ['Meet AgriHealth AI. Explore changes in your plants', 'with photo-based guidance for farmers and gardeners.']),
    ('01  Find your crop', '30 major Indian crops. One quick search.',
     'Search for your crop in English or Hindi. Choose from thirty major Indian crops. Select one to move straight to photos.',
     ['Search in English or Hindi. Choose from 30 major Indian crops.', 'Select a crop to move straight to Photos.']),
    ('02  Add clear photos', 'Gallery uploads + camera capture',
     'Add one to five clear photos from your gallery, or use your camera. Show leaves, stems, and affected areas in good light.',
     ['Add 1–5 clear photos from your gallery or camera.', 'Show leaves, stems and affected areas in good light.']),
    ('03  Share the context', 'A few details help explain the symptoms.',
     'Answer a few questions about symptoms, weather, and when changes began. Gemini reviews your photos and answers together for an A I assessment.',
     ['Answer questions about symptoms, weather and when changes began.', 'Gemini reviews the selected photos and your answers together.']),
    ('04  Understand the result', 'Possible causes. Practical next steps.',
     'Read the possible condition, visible signs, and safe crop care steps. Gemini can suggest conditions beyond the local disease guides. Download your P D F.',
     ['Read possible conditions, visible signs and safe crop-care steps.', 'Findings can go beyond local disease guides. Download a PDF.']),
    ('Carefully informed decisions', 'Keep observing. Ask an agricultural expert.',
     'A I guidance is not a confirmed diagnosis. Consult a local agricultural expert before treatment decisions. Start with clear photos, and keep monitoring your plants.',
     ['AI guidance is not a confirmed diagnosis. Consult an expert', 'before treatment decisions, and keep monitoring your plants.']),
]


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def text(draw, xy, value, size=24, fill=INK, bold=False):
    draw.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=fill)


def box(draw, xy, fill='white', outline='#cfe0d1', radius=18):
    draw.rounded_rectangle(xy, radius, fill=fill, outline=outline, width=2)


def leaf(draw, x, y, scale=1):
    draw.ellipse((x, y, x+110*scale, y+65*scale), fill='#51a571')
    draw.line((x+8*scale,y+57*scale,x+97*scale,y+12*scale), fill='#d4f2b4', width=max(2,int(4*scale)))


def render(index, elapsed):
    frame = Image.new('RGB', (W,H), BG)
    d = ImageDraw.Draw(frame)
    d.rectangle((0,0,W,9), fill=GREEN)
    text(d,(56,33),'AgriHealth AI',27,bold=True)
    text(d,(944,40),'HOW IT WORKS  /  01:00',17,fill=MUTED)
    text(d,(56,102),SCENES[index][0],42,bold=True)
    text(d,(58,166),SCENES[index][1],23,fill=MUTED)
    # All illustration elements are deliberately labelled as a walkthrough.
    box(d,(55,219,1225,575))
    text(d,(80,236),'WORKFLOW ILLUSTRATION',13,fill=MUTED)
    phase = min(1, elapsed/2)
    if index == 0:
        leaf(d,130,320,2.5)
        text(d,(480,294),'Look closer. Act thoughtfully.',32,bold=True)
        for j,label in enumerate(['Choose your crop','Add photos + context','Review AI guidance']):
            y=355+j*54
            d.ellipse((481,y,513,y+32),fill=GREEN)
            text(d,(490,y+2),str(j+1),19,fill='white',bold=True)
            text(d,(534,y),label,25)
    elif index == 1:
        box(d,(100,284,1180,337),fill='#f2f7f1')
        text(d,(121,295),'Search crops: '+ 'Potato'[:int(elapsed*3)],23)
        names=['Potato','Tomato','Rice','Wheat']
        for j,name in enumerate(names):
            x=100+j*277
            selected = j==0 and elapsed>2
            box(d,(x,365,x+250,522),fill='#e0f3e5' if selected else '#f7faf6',outline=GREEN if selected else '#cfe0d1')
            if j==0:
                d.ellipse((x+72,390,x+176,451),fill='#c5a579',outline='#96794e',width=2)
                for a,b in [(92,419),(128,403),(152,434)]:d.ellipse((x+a, b,x+a+5,b+5),fill='#876d46')
            else: leaf(d,x+75,391,.9)
            text(d,(x+65,476),name,23,bold=True)
        if elapsed>3:text(d,(899,543),'Selected → Photos',17,fill=GREEN,bold=True)
    elif index == 2:
        for j in range(5):
            x=101+j*220
            box(d,(x,299,x+198,482),fill='#e8f3e8')
            if elapsed>j*.5:leaf(d,x+39,352,1.05)
            text(d,(x+61,447),f'Photo {j+1}',17)
        text(d,(102,518),'1–5 photos  •  Gallery  •  Device camera  •  Multiple angles',24,bold=True)
    elif index == 3:
        for j,(q,a) in enumerate([('Visible symptoms','Leaf spots'),('Weather conditions','Humid'),('First noticed','A few days ago')]):
            y=290+j*80
            text(d,(100,y+12),q,23)
            box(d,(445,y,756,y+56),fill='#f2f7f1')
            text(d,(465,y+13),a,22)
        box(d,(823,294,1180,506),fill='#e0f3e5')
        text(d,(899,332),'Gemini AI',32,bold=True)
        text(d,(864,393),'Photos + answers',23)
        text(d,(872,440),'One assessment',22,fill=GREEN)
    elif index == 4:
        text(d,(98,284),'EXAMPLE REPORT SECTIONS',17,fill=GREEN,bold=True)
        for j,label in enumerate(['Possible condition','Observed signs','Safe next steps']):
            y=329+j*64
            box(d,(98,y,733,y+48),fill='#f2f7f1')
            text(d,(118,y+9),label,22)
        box(d,(805,311,1180,491),fill='#e0f3e5')
        text(d,(914,339),'PDF',40,bold=True)
        text(d,(837,406),'Download your report',23)
        text(d,(833,447),'Review it with an expert',19,fill=MUTED)
        text(d,(102,541),'Model confidence is not measured diagnostic accuracy.',17,fill=MUTED)
    else:
        text(d,(99,287),'AI-assisted information, not a diagnosis.',31,bold=True)
        for j,label in enumerate(['Consult a local agricultural expert before treatment.','Monitor changes and take clearer photos if needed.']):
            text(d,(100,356+j*53),label,24)
        box(d,(100,475,517,540),fill=GREEN,outline=GREEN)
        text(d,(128,491),'Check Plant Health →',26,fill='white',bold=True)
        text(d,(670,498),'greenhealth-indol.vercel.app',24,fill=GREEN)
    d.rounded_rectangle((56,593,1224,680),15,fill='#163d2b')
    for j,line in enumerate(SCENES[index][3]):
        font=ImageFont.truetype(FONT,23)
        width=d.textlength(line,font=font)
        text(d,((W-width)/2,607+j*31),line,23,fill='white')
    d.rectangle((56,698,1224,703),fill='#d7e5d8')
    d.rectangle((56,698,56+1168*(index*10+elapsed)/60,703),fill=GREEN)
    if elapsed<.4:
        frame=Image.blend(Image.new('RGB',(W,H),BG),frame,elapsed/.4)
    return frame


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='agri-tutorial-') as tmp:
        tmp=Path(tmp)
        audio=[]
        for index,scene in enumerate(SCENES):
            script=tmp/f'{index}.txt';script.write_text(scene[2],encoding='utf-8')
            raw=tmp/f'raw-{index}.wav';segment=tmp/f'{index}.wav'
            run('ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i',f'flite=textfile={script}:voice=slt',str(raw))
            info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-of','json',str(raw)]))
            duration=float(info['format']['duration'])
            tempo=duration/9.1
            print(f'Scene {index+1}: voice {duration:.2f}s → 9.1s (tempo {tempo:.2f})',flush=True)
            run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-af',f'atempo={tempo},adelay=350,apad,atrim=duration=10,loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1',str(segment))
            audio.append(segment)
        listing=tmp/'audio.txt'; listing.write_text('\n'.join(f"file '{p}'" for p in audio))
        narration=tmp/'narration.wav'
        run('ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(narration))
        render(0,2).save(OUT/'agrihealth-tutorial-poster.jpg',quality=90)
        process=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(narration),'-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart','-t','60',str(OUT/'agrihealth-tutorial.mp4')],stdin=subprocess.PIPE)
        for index in range(6):
            for f in range(FPS*10):
                process.stdin.write(render(index,f/FPS).tobytes())
            print(f'Rendered scene {index+1}/6',flush=True)
        process.stdin.close()
        if process.wait(): raise RuntimeError('Video encoding failed')
        print('Created',OUT/'agrihealth-tutorial.mp4',flush=True)


if __name__ == '__main__':
    main()
