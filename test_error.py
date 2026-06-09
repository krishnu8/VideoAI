from moviepy.editor import TextClip
try:
    t = TextClip('hello')
except Exception as e:
    import traceback
    traceback.print_exc()
