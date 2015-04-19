"Quicktalk" is a plugin for Blender which tries to do most of
the dull boring work for lip-synch for a character.

There's a video tutorial on the addon's website here:
http://tentacles.org.uk/quicktalk

First, make shape keys for the mouth shapes.
You'll need: AI, E, O, U, FV, L, MBP, WQ, ETC and the 
Basis should be a rest shape.

Give it an armature if you don't already have one. It needs an armature to
attach to the shape keys.

Put the 3d cursor near the object's face. It's where we'll 
create the panel of bones to control the shape-keys.
Click the "Build Shape-Key Panel Armature" button.
That'll build a panel of bones that control the shape-keys
Each bone can be rotated from 0 to 90 degrees like
a lever to control the expression. It'll build a lever
for EVERY shape key so you can include blinks or
smiles or whatever to get a lever for them too.

Select a script file.
Script files contain the dialogue the charters
in the scene speak. Lines with a single word
followed by a : mark changes in which character
is speaking. The armatures attached to the
character should be named the same as the
name in the script. Well, first few chars
have to match anyway.
Lines which aren't a single word followed by
a character are spoken by that character.
Example:

------------------

Monkey:
Hello I'm a monkey
Welcome to my cartoon

Dog:
Yes, and I'm a dog.

Monkey:
Welcome to my cartoon dog.

------------------

Click the "Guess Dialogue Markers" button.
This will try to guess where in the timeline
there's a change in who speaks and put markers
there. It will be wrong, so adjust them so 
they are right. You can make them yourself
if you need to for some reason, they are just 
normal markers but with names ending in "!D"

When they're right click the "Guess Line Markers"
which will add markers for each line that each
character speaks. Again they'll be wrong and
you'll have to adjust them. They end in "!L"

When they're right click the "Guess Word Markers"
button. It'll put markers for every spoken word.
There's more chance this will be more or less
right but still not much chance so fix 'em.
Word markers end in "!W"

Next you need to pick a dictionary that describes
which phonemes correspond to which words. You can
find a dictionary at the The CMU Pronouncing project
here:

http://www.speech.cs.cmu.edu/cgi-bin/cmudict

Once you've downloaded a dictionary, click the
browse button to tell the plugin where that is

Select an armature and click "QuickTalk Plot"
This will create f-curves for the scene which
change the x-rotation of the bones created in
the panel. There's a pretty good chance this
will look all right, but especially long words
or where there's pauses in speech it'll still
be wrong and you'll need to squash and scale
the f-curve to match.

If all that sounds long-winded, you do not understand
how damn tedious lip-synching is when you have
to do it literally frame by frame. 

