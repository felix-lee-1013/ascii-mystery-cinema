<div align="center">

# 🐰💜 ASCII Video Art

**every frame of a video, rebuilt out of letters and symbols instead of pixels**

</div>

---

### ✨ what is this?
A small coding art project that turns **any video** into ASCII art.
Give it a video, and it converts each frame into characters, so the
whole clip plays back as moving text.

I first made it for a Jungkook edit 💜, but it isn't limited to that.
**You can import any video of your own and convert it.**

### 🎬 how it works
1. 🎞️ the video is read frame by frame
2. 🌗 each frame is turned into grayscale (light and dark values)
3. 🔤 every small block of pixels is replaced with a character:
   dark areas get dense characters, light areas get sparse ones
4. 🖥️ the characters are put back together as frames and played as a video

### 🛠️ built with
- [Python]
- [library you used for reading video, e.g. OpenCV]
- [library for images or output, e.g. Pillow / NumPy]

### 🚀 how to use

```bash
# 1. clone this repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. install what it needs
pip install [your requirements]

# 3. add your video and run
python [your_script.py] [your_video_file]
```

Replace the last line with the real command from your code. Tell people
where the output is saved.

### 🎛️ settings you can change
- [character set / density]
- [output width, so more characters give more detail]
- [colour or black-and-white output]

*(keep only the ones your code actually supports)*

### 📸 preview
![preview](preview.gif)

### 📝 note
This is a fan-made art project, made for learning and fun.
Videos you convert belong to their original owners, so only use
videos you have the right to use. I haven't put the original video in
this repo.

---

<div align="center">

*made with 💜 by [Shravani](https://www.instagram.com/shraisqt)*

</div>
