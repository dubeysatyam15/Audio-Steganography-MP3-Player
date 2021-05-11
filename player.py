from tkinter import *
from tkinter import filedialog
import pygame
import time
import wave 
from mutagen.mp3 import MP3
import tkinter.ttk as ttk

root = Tk()

root.title('MP3 player')
root.geometry('500x400')

# Initialize Pygame
pygame.mixer.init()

# Create function to deal with time
def play_time():
	# chexk to see if song is stopped
	if stopped:
		return    # if stopped then it will come outside of play_time()
	# Grab current song time
	current_time = pygame.mixer.music.get_pos() / 1000
	# Convert song time to time format
	converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
	# Reconstruct song with directory strcutre
	song = playlist_box.get(ACTIVE)
	song = f'C:/mp3/audio/{song}.mp3'

	# Find Current Song length
	song_mut = MP3(song)
	global song_length
	song_length = song_mut.info.length
	# Convert to time format
	converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
	# Check to see if song is over
	if (int(song_slider.get()) == int(song_length)):
		stop()
	elif paused:
		# Check to see if paused, if so - pass
		pass
	else:
		# Move slider alonf 1 second at a time
		next_time = int(song_slider.get()) + 1
		# output new time value to slider, and to the length of the song
		song_slider.config(to=song_length,value=next_time)

		# Convert slider position to time format
		converted_current_time = time.strftime('%M:%S', time.gmtime(int(song_slider.get())))

		# Convert time to status bar
		status_bar.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length}  ')

	# Add current time to status bar
	if current_time > 0:
		status_bar.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length}  ')
	# Create loop to check the time every second
	status_bar.after(1000, play_time)


# Create function to add one song to playlist
def add_songs():
	song = filedialog.askopenfilename(initialdir='audio/', title='Choose A Song', filetypes=(('my3 files', '*.mp3'),) )
	# Strip out directory structure and .mp3 from the title of the song
	song = song.replace('C:/mp3/audio/', '')
	song = song.replace('.mp3', '')
	# Add to end of playlist
	playlist_box.insert(END, song)

def add_many_songs():
	songs = filedialog.askopenfilenames(initialdir='audio/', title='Choose A Song', filetypes=(('my3 files', '*.mp3'),) )
	# Loop through song list and replace directory
	for song in songs:
		# Strip out directory structure and .mp3 from the title of the song
		song = song.replace('C:/mp3/audio/', '')
		song = song.replace('.mp3', '')
		# Add to end of playlist
		playlist_box.insert(END, song)

def encode():
	#read wave audio file
	encode_song = wave.open(filedialog.askopenfilename(initialdir='audio/', title='Choose A Song', filetypes=(('wave files', '*.wav'),) ), mode='rb')
	#song = filedialog.askopenfilename(initialdir='audio/', title='Choose A Song', filetypes=(('wave files', '*.wav'),) )
	# Strip out directory structure and .wav from the title of the song
	#song = encode_song.replace('C:/mp3/audio/', '')
	#song = encode_song.replace('.wav', '')
	# Add to end of playlist
	#playlist_box.insert(END, song)

	
	# Read frames and convert to byte array
	frame_bytes = bytearray(list(encode_song.readframes(encode_song.getnframes())))
	file = filedialog.askopenfilename(initialdir='files/', title='Choose A file', filetypes=(('text files', '*.txt'),))
	file = open(file, 'r')
	re = file.read()
	# Append dummy data to fill out rest of the bytes. Receiver shall detect and remove these characters.
	re = re + int((len(frame_bytes)-(len(re)*8*8))/8) *'#'
	# Convert text to bit array
	bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in re])))

	# Replace LSB of each byte of the audio data by one bit from the text bit array
	for i, bit in enumerate(bits):
    		frame_bytes[i] = (frame_bytes[i] & 254) | bit
	# Get the modified bytes
	frame_modified = bytes(frame_bytes)

	# Write bytes to a new wave audio file
	with wave.open('C:/mp3/audio/song_embedded.wav', 'wb') as fd:
    		fd.setparams(encode_song.getparams())
    		fd.writeframes(frame_modified)
	message = 'Done!'
	my_label.config(text=message)
	encode_song.close()
	file.close()


def decode():
	#song = filedialog.askopenfilename(initialdir='audio/', title='Choose A Song', filetypes=(('wave files', '*.wav'),) )
	# Strip out directory structure and .mp3 from the title of the song
	#song = song.replace('C:/mp3/audio/', '')
	#song = song.replace('.wav', '')
	# Add to end of playlist
	#playlist_box.insert(END, song)
	
	decode_song = wave.open(filedialog.askopenfilename(initialdir='audio/', title='Choose A Song', filetypes=(('wave files', '*.wav'),) ) , mode='rb')
    # Convert audio to byte array
	frame_bytes = bytearray(list(decode_song.readframes(decode_song.getnframes())))
    # Extract the LSB of each byte
	extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    # Convert byte array back to string
	string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
	# Cut off at the filler characters
	decoded = string.split("###")[0]
	# Create a file for decoded message to be displayed
	file = open('files/Decode_message.txt', 'w')
	# Print the extracted text
	file.write(decoded)
	decode_song.close()
	file.close()

# Create function to delete one song
def delete_song():
	# Delete hightlighted song from playlist
	playlist_box.delete(ANCHOR)

# Create function to delete many songs
def delete_all_songs():
	# Delete all songs from the playlist
	playlist_box.delete(0, END)

# Create Play Function
def play():
	# Set stopped to false since a song is now playing
	global stopped
	stopped = False
	# Reconstruct song with directory strcutre
	song = playlist_box.get(ACTIVE)
	song = f'C:/mp3/audio/{song}.mp3'
	# Load song with pygame mixer
	pygame.mixer.music.load(song)
	# Play song with pygame mixer
	pygame.mixer.music.play(loops=0) # To play song once
	# get song time
	play_time()

# Create stopped variable
global stopped
stopped = False
# To stop a music 
def stop():
	pygame.mixer.music.stop()
	# Clear playlist bar
	playlist_box.selection_clear(ACTIVE)
	status_bar.config(text='')
	# set stopped variabel to true
	global stopped
	stopped = True

# Create paused vatiable
global paused
paused = False

# To pause a music
def pause(is_paused):
	global paused
	paused = is_paused
	if paused:
		pygame.mixer.music.unpause()
		paused = False
	else:
		pygame.mixer.music.pause()
		paused = True

# Create volume function
def volume(x):
	pygame.mixer.music.set_volume(volume_slider.get())

# Create a slider function for song positioning
def slide(x):
	# Reconstruct song with directory strcutre
	song = playlist_box.get(ACTIVE)
	song = f'C:/mp3/audio/{song}.mp3'
	# Load song with pygame mixer
	pygame.mixer.music.load(song)
	# Play song with pygame mixer
	pygame.mixer.music.play(loops=0, start=song_slider.get()) 

# Create function to play next song
def next_song():
	# reset slider position and status bar
	status_bar.config(text='')
	song_slider.config(value=0)
	# Get curreny song number
	next_one = playlist_box.curselection()
	# Add one to the tuple/list to play the next song
	next_one = next_one[0] + 1
	# Grab the song title from the playlisy
	song = playlist_box.get(next_one)
	# Add directory structure stuff to the song
	song = f'C:/mp3/audio/{song}.mp3'
	# Load song with pygame mixer
	pygame.mixer.music.load(song)
	# Play song with pygame mixer
	pygame.mixer.music.play(loops=0) # To play song once
	# clear active bar in playlist
	playlist_box.selection_clear(0, END)
	# Move active bar to next song
	playlist_box.activate(next_one)
	# set the active bar to next song
	playlist_box.selection_set(next_one, last=None)
	# We need to change the selection bar to move to next song.

def previous_song():
	# reset slider position and status bar
	status_bar.config(text='')
	song_slider.config(value=0)
	# Get curreny song number
	next_one = playlist_box.curselection()
	# Add one to the tuple/list to play the next song
	next_one = next_one[0] - 1
	# Grab the song title from the playlisy
	song = playlist_box.get(next_one)
	# Add directory structure stuff to the song
	song = f'C:/mp3/audio/{song}.mp3'
	# Load song with pygame mixer
	pygame.mixer.music.load(song)
	# Play song with pygame mixer
	pygame.mixer.music.play(loops=0) # To play song once
	# clear active bar in playlist
	playlist_box.selection_clear(0, END)
	# Move active bar to next song
	playlist_box.activate(next_one)
	# set the active bar to next song
	playlist_box.selection_set(next_one, last=None)
	# We need to change the selection bar to move to previous song.

# Create main frame
main_frame = Frame(root)
main_frame.pack(pady=20)

# Create Playlist Box
playlist_box = Listbox(main_frame, bg='black', fg='green', width=60, selectbackground='green', selectforeground='black')
playlist_box.grid(row=0, column=0)

# Create volumer slider frame
volume_frame = LabelFrame(main_frame, text='Volume')
volume_frame.grid(row=0, column=1, padx=20)

# create volume slider
volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=VERTICAL, length=125, value=1, command= volume)
volume_slider.pack(pady=10)

# create song slider
song_slider = ttk.Scale(main_frame, from_=0, to=100, orient=HORIZONTAL, length=360, value=0, command= slide)
song_slider.grid(row=2, column=0, pady=20)

# Define Button Images for controls
back_btn_img = PhotoImage(file="images/back50.png")
forward_btn_img = PhotoImage(file="images/forward50.png")
play_btn_img = PhotoImage(file="images/play50.png")
pause_btn_img = PhotoImage(file="images/pause50.png")
stop_btn_img = PhotoImage(file="images/stop50.png")
# Create Button Frame
control_frame = Frame(main_frame)
control_frame.grid(row=1, column=0, pady=20)

# Create Play/Stop etc Buttons
back_button =  Button(control_frame, image=back_btn_img, borderwidth=0, command=previous_song)
forward_button = Button(control_frame, image=forward_btn_img, borderwidth=0, command=next_song)
play_button = Button(control_frame, image=play_btn_img, borderwidth=0, command=play)
pause_button = Button(control_frame, image=pause_btn_img, borderwidth=0, command=lambda: pause(paused))
stop_button = Button(control_frame, image=stop_btn_img, borderwidth=0, command=stop)

back_button.grid(row=0, column=0, padx=10)
forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=2, padx=10)
pause_button.grid(row=0, column=3, padx=10)
stop_button.grid(row=0, column=4, padx=10)

# Create Main Menu
my_menu = Menu(root)
root.configure(menu=my_menu)

# create add song menu dropdowns
add_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label='Add Songs', menu=add_song_menu)
#Add one song to the playlist
add_song_menu.add_command(label='Add one song to playlist', command=add_songs)
# Add many song to the playlist
add_song_menu.add_command(label='Add many songs to playlist', command=add_many_songs)
# Encode the message in the song
add_song_menu.add_command(label='Message encode', command=encode)
# Decode the message in the song
add_song_menu.add_command(label='Message decode' , command=decode)

# Create Delete soong menu dropdowns
remove_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label='Remove songs', menu=remove_song_menu)
remove_song_menu.add_command(label='Delete a song from platlist', command=delete_song)
remove_song_menu.add_command(label='Delete all songs from platlist', command=delete_all_songs)

# Create status bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

# Temp label
my_label = Label(root, text='')
my_label.pack(pady=20)

root.mainloop()