# pyRunner @ Python mit dem Raspberry Pi SEP
###### last updated: 2016-05-22 at 9 pm (UTC +2)

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
RenderThread in 'renderthread.py' does all the screen refresh's, screen
size calculation etc. If you want your drawings to get rendered utilize this
function. The RenderThread, as all other classes get's instantiated in
'mainwindow.py'.

### Important RenderThread functions:
#### ```python blit(surface, pos, center=False)```
Requires two arguments. The surface you drew onto which you want to get
rendered to the main screen (pygame.Surface) and either a position
tuple (int, int) with the offset of your surface on the screen ((0, 0) if
your surface and the screen have the same size) or a centered boolean, which
will cause your surface to be centered on the main screen (x and y).
If it's centered you should provide None as position to make it clear for others
that you don't intend to use it.


#### ```python add_rect_to_update(rects, surface=None, pos=None, centered=None)```
The RenderThread _only_ updates the screen part that changed. Therefore
_all_ of your functions have to collect the rects that changed and return it
to the main class ('mainwindow.py'), where it will get sent to this function.
No matter if you draw on a surface that's the same size as the screen size or
not, it is suggested to provide the surface you drew to as well as either
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
	# draw my classes stuff
	rects = MyClass.draw_something(value)

	'''render_thread is the local instance of the RenderThread'''
	# draw the surface centered to the main screen
	render_thread.blit(MyClass.surface, None, True)

	# tell it to update the whole screen -- use only if the whole screen changed
	render_thread.render_thread.refresh_screen(True)
	# tell it to update only the changed parts (way less cpu intensive)
	render_thread.add_rect_to_update(rects)
```

