**WARNING** This is very, very early work. It is probably **not useful** to you at this point.

# picdedupe

A command line tool (as well as a re-usable library) to aid in dealing with a large number of incoming pictures (e.g. from a camera or phone), before adding them to your collection.

## The Sales Pitch

Imagine you have one or more nicely kept collections of pictures (e.g. your family pics). Now imagine you find an SD card around the house, or you want to back up your mom's iPhone. You might want to add some of these pictures to your collection. But you probably don't want to add all pictures. More specificially: 

- You DON'T want exact duplicates.
- You DON'T want lower quality images of what you have already:
  - JPEG versions (when you HEIC).
  - Lower resolution or cut-down versions.
- You DON'T want screenshots.
- You MAY NOT want 10 pictures of the exact same thing, even if they are slightly different.
- You DON'T want the .mov part of a Live Photo you have removed.

picdedupe helps you with all of these, in modular, expandable way! 

It will try to do The Right Thing™. But you can change this if you don't agree. You can make it ask you for every individual case as well!

picdedupe is fast! On its first run, it needs to index your collection, which might take a while, depending on the size. But after that, it can reuse that index to cut down on redundant steps.


## Fixits

picdedupe has a modular architecture. The common problems described above are detected by a `Fixit`. Each one can offer one or more solutions in the form of a `FixitAction`. You can easily write these these yourself. But picdedupe already comes with a few out-of-the-box:

- Exact duplicate file
  - default: move the candidate file to `./_dupes`, leaving a note
  - or: soft-delete the candidate file to `./_trash`
  - or: ignore and do nothing

- The file date does not match the image date
  - default: update the file date to match
  - or: ignore and do nothing

- Similar image, worse quality
  - default: move the candidate file to `./_similar`, leaving a note
  - or: soft-delete the candidate file to `./_trash`
  - or: ignore and do nothing

- Similar image, better quality
  - default: ignore and do nothing
  - or: add the file into the collection & move the collection file to `./_similar`, leaving a note

- Found the `.mov` file of a Live Photo (and the `.jpg` is there)
  - default: Rename the file to `.jpg.mov`
  - or: move to `./_live` so we can double-check if we like them.
  - or: soft-delete the candidate file to `./_trash`
  - or: ignore and do nothing

- Found the `.mov` file of a Live Photo (and the `.jpg` is missing!)
  - default: soft-delete the candidate file to `./_trash`
  - or: ignore and do nothing

- Found a `.png` file (most likely a screenshot)
  - default: soft-delete the candidate file to `./_trash`
  - or: ignore and do nothing


## Series & Groups

picdedupe can work on individual files. But it is also aware of files belonging together. 

A `FileGroup` is a collection of files that represent the same image. For example:
- A `.jpg` and `.mov` mag form a single Live Photo.
- A `.jpg` and its RAW should probably stay together.

A `FileSeries` is a collection of `FileGroup` that are taken around the same time, at the same location, by the same camera. The file numberings cannot have gaps. 

Series allow picdedupe to make bigger decisions. For example, if it finds exact dupes of multiple files in the same `FileSeries`, it might assume that all files in it were already considered. And so it might consider the entire `FileSeries` as a dupe (even though not all the files can be found in the collection), saving you a lot of time!

Groups allow for similar operations accross the group. Examples:
- Rename the `.mov` part of a Live Photo to `.jpg.mov`
- Rename a `.jpg` version of an exist HEIC to `.heic.jpg`
- Treat them as one when renaming, moving or deleting.


## Configurable & Modular & Exandable

- YOU set the default actions for all encountered scenarios.
- YOU can write your own custom `Fixit`
- YOU can write your own custom `FixitAction`
- YOU can write another (GUI?) frontend
- etc...

And if you do, feel free to add them into this project for everyone to use!


**WARNING:** THIS IS NOT READY TO BE USED BY ANYONE.

**WARNING:** USE THIS AT YOUR OWN RISK (OF LOSING YOUR PICTURES)! MAKE BACKUPS!

