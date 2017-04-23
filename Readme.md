# pyRunner @ Python mit dem Raspberry Pi SEP

PyRunner is a Remake of classic platformer game Loderunner. It was developed during a semester-long class project by a group of students from the University of Munich. To fulfill the class requirements, PyRunner is optimized for the Raspberry PI hardware and features gamepad support with local multiplayer.

##Running the game

## Setup
Um das spiel zu starten werden die folgenden Libs benötigt
- PyGame
- ZeroConf
- pyTmx
- Mastermind

Mastermind ist bereits inkludiert.
Pygame muss selbst installiert/kompiliert werden.
Die restlichen Libraries können mit `pip3 install -r requirements.txt` installiert werden

##Starten
Das Spiel wird mit `python3 pyRunner.py` gestartet

## Team Communication:

### Slack
- https://pyberries.slack.com

### Trello
- https://trello.com/b/VtSg0iUi/



## Documentation and Codeguidelines
- regulary check this file for updates or update it yourself
    - https://github.com/gitlabhq/gitlabhq/blob/master/doc/markdown/markdown.md
- use PEP-8 named functions, classes etc.
    - https://www.python.org/dev/peps/pep-0008/
- write Google Style docstrings for all functions you write
    - http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
- create own branches for new features
    - don't push to master (ask @fahrenwalde to pull/merge your changes)
        - Exception: this file should be updated by @all @master
    - the 'stable' branch is write protected for developers
        - https://about.gitlab.com/2014/11/26/keeping-your-code-protected/
- test your code and watch cpu usage!!
    - try to provoke crashes through random/fast user input
    - add sanity checks at critical locations
- basic usage of the Render and Music Thread are below
    - make sure your drawing functions return their rects (in a list or single rect) to the main function
        - this allows the main function to pass it to the Render Thread for partial screen updates
    - draw to an own surface, not the main screen
        - blit your surface to the main screen from the main through the RenderThread
            - the main function has to be able to get your screen from your class
        - make sure your surface is ~~resizable/exchangable if the screen/window size changes~~ working with different resolutions
            - ~~I might remove the resize window feature and add the resolution selection in windowed mode~~
            - this ~~would~~ ensures that the screen resolution doesn't change if the game is running (restarts on resolution change)



## Main Class
The main class to run until this whole project is packed up is the
'pyRunner.py'. Here all sub threads get instantiated, settings are read
and written and passed to other classes etc.

## Important Classes:
## RenderThread
RenderThread in 'pyrunner_classes/render_thread.py' is a daemon thread that does all
the screen refreshes, screen size calculation etc.
If you want your drawings to get rendered utilize this class.

The RenderThread, as all other classes get's instantiated in 'pyRunner.py'.

### Important RenderThread functions:
```python
def blit(surface, pos, center=False):
```
Requires two arguments. The surface you drew onto which you want to get
rendered to the main screen (pygame.Surface) and either a position
tuple (int, int) with the offset of your surface on the screen ((0, 0) if
your surface and the screen have the same size) or a centered boolean, which
will cause your surface to be centered on the main screen (x and y).
If it's centered you should provide None as position to make it clear for others
that you don't intend to use it.


```python
def add_rect_to_update(rects, surface=None, pos=None, centered=None):
```
The RenderThread _only_ updates the screen parts that have changed. Therefore
_all_ of your functions have to collect the rects that changed and return it
to the main class ('pyRunner.py'), where it will get sent to this function.
No matter if you draw on a surface that's the same size as the screen size or
not, it is suggested to provide the surface you drew to as well and either
the position or centered value you used with the blit function.

The RenderThread is only able to get the correct rects to update positions
if the surface is provided. Because it provides lot's of different viewing
options - even if those 3 values are declared optional - it need's those values
for screen updates on Linux to function properly.

Note: rects can either be a single rect or a list of rects
	  but not a list with lists of rects

Example usage
```python
class MyClass(object):

	__init__(self, surface, ...):
	# it is important to pass a surface to your class where it can draw on to
		self.surface = surface

	def draw_something(self, values):
		# create an empty list to store all objects
		rects_to_return = []
		# if you only draw one item you can return it's Rect without list

		# add each item you drew to it (use .get_rect() etc. if its no rect)
		rects_to_return.append(pygame.draw....)

		# return the list of rects to the main function
		return rects_to_return
```

and in the 'pyRunner.py'

```python
def do_my_stuff():
	# create an instance of your class, if it's used more often think
	# about saving it in a global variable
	global my_class
	my_class = MyClass(Pygame.Surface, values)
	# draw my classes stuff
	rects = my_class.draw_something(value)

	pyRunner.py
	# draw the surface centered to the main screen
	render_thread.blit(my_class.surface, None, True)

    # tell it to update only the changed parts (way less cpu intensive)
	render_thread.add_rect_to_update(rects, my_class.surface, None, True)

	# tell it to update the whole screen -- use only if the whole screen changed!!
	render_thread.refresh_screen(True)
```


## MusicMixer
MusicMixer in 'pyrunner_classes/sound_thread.py' is a daemon thread that takes care of all
the music and sound output.

It creates additional pygame.mixer.Channels if the current amount of
sounds exceeds the available channels - therefore no sound get's lost and
no sound lag should occur.

As any other classes/threads it get's instantiated at the main class.

### Important MusicMixer functions:
```python
def play_sound(file)
```
This function takes either a string with the file name of a sound file
in _/resources/sound_fx/_ or a pygame.mixer.Sound file and passes it to the next
available channel to be played. If there's not enough channels it will
dynamically create more.


```python
def get_full_path_sfx(file)
```
returns the full path for a sound file located in _/resources/sound_fx/_ to
be used if you intent to play this sound more than once -- you can get the
full path and create a stored pygame.mixer.Sound which you can pass to
MusicMixer.play_sound each time.


Example usage
```python
pyRunner.py
music_thread.play_sound('my_super_loud_sound.wav')

# or the disk I/O saving solution
global super_sound
super_sound = pygame.mixer.Sound(music_thread.get_full_path_sfx('sound.wav'))
music_thread.play_sound(super_sound)
```

There are similar functions for *Music Playback* as well:
```python
def background_music(self, file_loops)
```
this is the main object to add a music file to the music playlist.
Other than the play_sound option this is no function it's rather an object
accepting a tuple as arguements:

```python
music_thread.background_music = ('my_sweet_music.mp3', loops)
```
note that the loops is always one more as you expect it to be
(3 loops 4 times etc). -1 would cause an endless loop but it's suggested not
to use this -- the playlist get's repeated so if you want to endless loop a
song, just don't add another one! (and use clear_background_music before
if needed).


```python
def clear_background_music()
```
is the only way to stop an endless looping music file.
This option clears the current playlist as well so it's suggested to
call this if you change the level and want to change the sound atmosphere.

```python
def get_full_path_music(file)
```
is the same as get_full_path_sfx above but files are located in
_/resources/music_

```python
@property
def play_music()
```
You can use this to start/stop music playback. You should only use this
to temporary disable playback if it was enabled before - because this value
is one that can be set by a user (in the settings - audio - music on/off).
If this is disabled the user probably doesn't want to listen to any music.


Example usage
```python
def my_super_duper_playlist():

	# add some music to the playlist
	# just play this once as a small starter
    music_thread.background_music = ("Modern Talking - You're my heart, you're my soul.mp3", 0)
    # loop those classics 6 times
    music_thread.background_music = ("Modern Talking - Cherry cherry lady.mp3", 5)
    music_thread.background_music = ("Kiss - I was made for lovin' you.mp3", 5)
	# loop my favorite song 10 times
	music_thread.background_music = ("Rick Astley - Never Gonna Give You Up.mp3", 9)

```
this will play those songs in the order they were added, repeat each song
according to it's loop setting (+1) and start again at the beginning if
everything was played.

This will continue until
```python
	# either
	music_thread.clear_background_music()
	# or
	music_thread.play_music = False
```
are called / set.


