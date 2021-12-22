# Echo Programming Language

## Working principle

Echo manipulates an audio source which can produce sounds in four different directions. Those sounds have a constant intensity, specified when they're created, and will bounce off a wall created when sending the sound, at a specified distance. The sounds always move at one unit per instruction. They start one unit after the source, and start to move only after the next instructions.
Walls are always situated between two units, which means the movement of a sound follows a path as follows (`X` is the audio source, `o` is the sound, and `|` is the wall) :

```
Xo   |
X o  |
X  o |
X   o|
X  o |
X o  |
Xo   |
X    |
```

When a sound gets back to the source, it is absorbed and destroyed. At every instruction, the audio source can receive up to 4 different sounds. The intensities of those sounds are added up (modulo 256) and this sum is called the "sound sum" and used in some instructions.

### Walls

There are two "kinds" of walls : the ones associated with a sound, and the independant ones. A wall associated with a sound disappear when the sound has bounced off it or has been destroyed. A sound always bounces off the first wall on its way, which means a wall may bounce a sound it was not destined for. An independant wall disappears when it has been hit by any sound.
In the following example, `o` is the sound associated with the wall `|`, and `u` the one associated with `/`. We can see that `o` will bounce off `/` and not its own wall.

```
X   o    |
Xu   o / | (creation of a second sound which wall is closer than the first)
X u   o/ |
X  u o / |
```

When a sound is moving towards the source, it does not interect with walls anymore.

## Instructions

| Instruction| Description| Parameter 1| Parameter 2| Parameter 3|
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|------------------------------------------|-----------------------------|
| nop       | Does nothing (it still counts as a one or more steps for the sounds).|Number of steps to nop (> 0).<br>[Optional, default value is 1]| ---                                      | ---                         |
| send       | Send one or more sounds. The sounds all have the same intensity and their walls are at the same distances, but they can be sent in different directions.| Directions (4 LSB)| Wall distance (> 0)| Intensity (> 0)|
| redirect| Send the sound sum (modulo 256) or its complementary modulo 256 in the specified directions and distance.| Directions (4 LSB)| Wall distance (> 0)| 0 on the LSB to send the sum, and 1 to send its complementary.<br>[Optional, default value is 0] |
| print| Print the sound sum directly or as an ASCII character.| ---| ---| --- |
| condition | According to parameter 1, execute (or not) the n next instructions if the sound sum fulfills the condition compared to the specified value.| Condition (4 LSB) | Value| Instructions count (> 0) |
| for | Repeat the n next instructions as many times as specified. <br> When this instruction is completed, the instruction pointer will be at the next one, meaning the repeated instructions may be executed once more. | Repetitions count (> 0)| Instructions count (> 0) | ---|
| input| Send a sound in the specified directions and distance with an intensity equals to the ASCII value of the character typed by the user.| Direction (4 LSB)| Wall distance (> 0)| ---|
| wall|Create an independant wall in the specified directions and distance. They will disappear after one bounce.|Direction (4 LSB)|Distance (> 0)| ---|
| exit| Exit the program.| ---| ---| ---|

**Note**
Two more instructions exist : `predirect` et `pcondition`, which are a combination of `print` and their version without the `p`. Their parameters are exactly the same as the base version.

### Code

The code is written with one instruction per line only. One line of code consists of one word (case insensitive) followed by up to 3 parameters.  The parameters are separated from each other and from the command by a space (` `). They are always written in base 10 and, unless otherwise stated, are included in the interval [0 ; 255]. When an instruction require less than 3 parameters, more can be writtent but they will be ignored.
Every line starting with a character which is neither a letter nor a whitespace is considered as a comment.

### Directions

To define directions, the four LSB are used, each one indicating if the sound should be sent in that direction. At least of one those four bits must be 1 for the code to be valid.
For example, if a direction is `10` (or `00001010` in binary), it means the sound should be sent in two directions (of index 4 and 2).

### Conditions

Parameter one of a condition is defined as follows in binary :

```
xxxxDise
```
Where :
 - `x` : not used, can be anything.
 - `D` : 0 if we should not execute instructions only when the condition is fulfilled, and 1 otherwise.
 - `i` : 1 if the condition should check if the sound sum is strictly smaller than the specified value.
 - `s` : 1 if the condition should check if the sound sum is strictly greater than the specified value.
 - `e` : 1 if the condition should check if the sound sum is equal to the specified value.

When multiple bits are 1, the result is a logical OR of all of them. Conditions can then be combined to test for other conditions.
For example :
 - `xxxx1001` : instructions will be executed only if the sound sum if equal to the value.
 - `xxxx0100` : instructions will not be executed is the sound sum is stricly smaller than the value.
 - `xxxx1011` : instructions will be executed if the sound sum if greater than or equal to the value.
 - `xxxx0110` : instructions will not be executed if the sound sum is either stricly greater or strictly smaller than the value (equivalent to inequality).

**Note** : `i=s=e=0` is an invalid condition.

## Examples

```ini
send 1 3 65
nop 5
print
```
Send a sound with intensity 65 in direction 1, wait 5 steps, and then print the sound sum (which will be equal to 65, ASCII code for 'A').


```ini
send 1 3 65
nop
send 2 2 32
nop 3
print
```
Send one sound with intensity 65 in direction 1, and another in direction 2 with intensity 32 after one more step. Wait 3 steps, then print the sound sum which will be 65+32.

### Hello, world!

```ini
send 1 1 72
send 2 1 101
print
print
send 3 2 108
wall 1 1
print
send 1 1 111
print
print
send 1 1 44
send 2 1 32
print
print
send 1 1 119
send 2 1 111
print
print
send 1 1 114
send 2 1 108
print
print
send 1 1 100
send 2 1 33
print
print
```

### More complicated

```ini
send 2 4 1
nop

for 13 9
predirect 8 5
nop 5
redirect 1 8
nop 3
redirect 6 9
wall 4 3
nop 4
redirect 2 3
nop 5
```
Prints the start of the Fibonacci sequence.

```ini
send 2 3 3 ; Value of A
nop
send 8 2 255
send 1 4 5 ;Value of B


nop 2
for 255 14

redirect 6 12
wall 4 1

condition 2 0 5
nop 2
redirect 3 6
wall 2 1
print
exit

nop
send 8 4 255
redirect 3 6
wall 2 1
redirect 4 6
nop 4
```

Prints the result of A * B.

# Interpreter

To use the interpreter, just run the file `main.py` inside the `Interpreter` folder with the Echo code as its first argument :
```
python3 Interpreter/main.py examples/fibonacci.ech
```
Another argument can be added : `-p` (or `--printstyle`) which can have one of two values : `ascii` or `numbers`. It just dictates how the output is presented to the user.
It is optional, and its default value is `ascii`.

Furthermore, the interpreter will create a file, called `renders.txt`, which contain a visualisation of what happened during the code execution. For example, after interpreting the second example program, it gives :

```
=================== send 1 3 65
0o  |        o = 65
 ··········
1          
X   Sound sum : 0
2          
 ··········
3          
===================
=================== nop   
0 o |        o = 65
 ··········
1          
X   Sound sum : 0
2          
 ··········
3          
===================
=================== send 2 2 32
0  o|        o = 65
 ··········
1o |         o = 32
X   Sound sum : 0
2          
 ··········
3          
===================
=================== nop 3  
0 o          o = 65
 ··········
1 o|         o = 32
X   Sound sum : 0
2          
 ··········
3          
===================
=================== nop 3  
0o           o = 65
 ··········
1o           o = 32
X   Sound sum : 0
2          
 ··········
3          
===================
================== nop 3  
0          
 ··········
1          
X   Sound sum : 97
2          
 ··········
3          
==================
================= print   
0          
 ··········
1          
X   Sound sum : 0
2          
 ··········
3          
=================
```