# pyRunner @ Python mit dem Raspberry Pi SEP
###### last updated: 2016-05-23 at 00:05 am (UTC +2)

## TODO
- [ ] create main class / function @fahrenwalde
	- [ ] create object orientated menu @fahrenwalde
		- [ ] New Game
			- [ ] Single Player
				- [ ] New Game
				- [ ] Resume
				- [ ] Difficulty
			- [ ] Multiplayer
				- [ ] Start Game
				- [ ] cooperative (local and LAN)
				- [ ] versus (only LAN)
				- [ ] Join Game
		- [ ] Settings
			- [x] Audio @fahrenwalde
				- [x] Music on/off and volume @fahrenwalde
				- [x] Sound FX on/off and volume @fahrenwalde
			- [ ] Controls @fahrenwalde
				- [ ] Keyboard Player 1/2
				- [ ] Joystick (optional)
				- [ ] Left
				- [ ] Right
				- [ ] Up
				- [ ] Down
				- [ ] Shoot/Dig Left
				- [ ] Shoot/Dig Right
				- [ ] Interact
				- [ ] ...
			- [x] Video @fahrenwalde
				- [x] fullscreen on/off @fahrenwalde
				- [x] screen resolutions @fahrenwalde
				- [x] switch resolutions @fahrenwalde
				- [x] show fps @fahrenwalde
		- [x] Exit for top level, Back for sub menus @fahrenwalde
	- [x] create main render thread @fahrenwalde
	    - [x] reduce screen flickering @fahrenwalde
	    - [x] avoid crashes @fahrenwalde
	    - [x] watch cpu usage @fahrenwalde
	    - [x] screen modes @fahrenwalde
	        - [x] windowed @fahrenwalde
	        - [x] fullscreen @fahrenwalde
	        - [x] fullscreen with smaller main surface (don't switch resolution) @fahrenwalde
	    - [x] allow window resizing @fahrenwalde
	        - [ ] fix background surface resizing bug @fahrenwalde
	    - [x] only update changed rects @fahrenwalde
	    - [x] update the whole screen if needed @fahrenwalde
	    - [x] allow other classes to blit surfaces to the screen @fahrenwalde
	        - [x] calculate offsets for smaller surfaces @fahrenwalde
	- [x] create sound and music thread @fahrenwalde
	    - [x] allow sound playback @fahrenwalde
	        - [x] create more sound channels if too many sounds are played at once @fahrenwalde
	    - [x] allow music playback @fahrenwalde
	        - [x] playlist and loops @fahrenwalde
	    - [x] allow user to mute music/sfx and change the volume @fahrenwalde
	- [x] add config parser to read and write configs @fahrenwalde
		- [x] add screen related settings @fahrenwalde
		- [x] add audio related settings @fahrenwalde
		- [ ] add control related settings
	- [ ] create main network thread @fahrenwalde @wankmueller
	    - [ ] exchange player and enemy positions (x, y) [old -> new]
		- [ ] UDP for fast response
		- [ ] TCP for a synched state
		- [ ] Zeroconf/Bonjour network browser (optional) @fahrenwalde
- [ ] game
	- [ ] create basic game rendering @wankmueller @ghebreweldi @grombach
	    - [ ] don't use fps for movement speed
	        - [ ] use a seperate clock!! (fps should be changeable)
		- [ ] player can move
			- [ ] left/right
			- [ ] up/down
		- [ ] colission detection
		- [ ] add enemies
			- [ ] shortest path algorithm thread @fahrenwalde @wankmueller
		- [ ] add extras (optional)
			- [ ] weapon's
				- [ ] honey to glue enemies to non diggable grounds
	- [ ] add tile map support @wankmueller @ghebreweldi @grombach
		- [ ] different tiles for different floors
			- [ ] diggable
				- [ ] grass
				- [ ] dirt
			- [ ] non digabble
				- [ ] stone
				- [ ] steel/metal
		- [ ] make tilemaps adjustable to screen size @fahrenwalde
	- [ ] Sprites
	    - [ ] Players
	    - [ ] Enemies
	- [ ] Multiplayer support
		- [ ] test game modes
		- [ ] 2 players coop (local and LAN) (priority!)
		- [ ] 2 - 4 players versus in teams (optional)
		    - [ ] enemy team can't see holes in the ground
		- [ ] players can interact
		    - [ ] taunt
		    - [ ] carry/throw each other around (optional)
		- [ ] scoreboard
		    - [ ] global high score (top 10)
		    - [ ] Players can set their name
		    - [ ] teams switch role each round (enemy becomes attacker and the other way round)
	    - [ ] both attackers need to collect specific keys to get to the next level
	    - [ ] the players have to collect all coins
	        - [ ] every coin increases the players/teams score
	        - [ ] enemies can collect one coin each (or more in mp?)
	            - [ ] which drops when they fall into a hole
	- [ ] add more levels with Tiled @grombach
		- [ ] Indiana Jones style like Lode Runner - The Legend returns
	- [ ] refine graphics and sprites @ghebreweldi
- Documentation and Codeguidlines
    - use PEP-8 named functions, classes etc. @all
    - write Google Style docstrings for all functions you write @all
    - test your code and watch cpu usage @all
        - try to provoke crashes through random/fast user input @all
        - add sanity checks at critical locations @all
- [ ] package things up to deploy @wankmueller
    - [ ] maintain Python 2.7 compatibility @all


## Requirements
This game is tested with Python 3.5.1 and Python 2.7.11, both with the
latest version of PyGame (1.9.2) installed. Although Python 2 is no
requirement at the SEP, it would be great if we can keep compatibility,
as most PyGame installers are still linked against Python 2.

## Main Class
The main class to run until this whole project is packed up is the
'mainwindow.py'. Here all sub threads get instantiated, settings are read
and written and passed to other classes etc.

## Important Classes:
## RenderThread
RenderThread in 'renderthread.py' is a daemon thread that does all
the screen refreshes, screen size calculation etc.
If you want your drawings to get rendered utilize this class.

The RenderThread, as all other classes get's instantiated in 'mainwindow.py'.

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
to the main class ('mainwindow.py'), where it will get sent to this function.
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

	[.. init etc .. ]
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

and in the 'mainwindow.py'

```python
def do_my_stuff():
	# create an instance of your class, if it's used more often think
	# about saving it in a global variable
	global my_class
	my_class = MyClass(Pygame.Surface, values)
	# draw my classes stuff
	rects = my_class.draw_something(value)

	'''render_thread is the local instance of the RenderThread'''
	# draw the surface centered to the main screen
	render_thread.blit(my_class.surface, None, True)

	# tell it to update the whole screen -- use only if the whole screen changed
	render_thread.render_thread.refresh_screen(True)
	# tell it to update only the changed parts (way less cpu intensive)
	render_thread.add_rect_to_update(rects, my_class.surface, None, True)
```


## MusicMixer
MusicMixer in 'musicthread.py' is a daemon thread that takes care of all
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
# music_thread is the local instantiated object in 'mainwindow.py'
music_thread.play_sound('my_super_loud_sound.wav')

# or the disk I/O saving solution
global super_sound
super_sound = pygame.mixer.Sound(music_thread.get_full_path_sfx('sound.wav'))
music_thread.play_sound(super_sound)
```

There are similar functions for *Music Playback* as well:
```python
def background_music(self, file_loops):
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
def play_music():
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
    # loop this classic 6 times
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
	# ...
	music_thread.clear_background_music()
	# or
	music_thread.play_music = False
```
are called / set.


