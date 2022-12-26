**WARNING** This is very, very early work. It is probably **not useful** to you at this point.

# picdedupe

A command line tool (as well as a re-usable library) to aid in dealing with a large number of incoming pictures (e.g. from a camera or phone), before adding them to your collection.

Imagine you have one or more nicely kept collections of pictures (e.g. your family pics). Now imagine you want to find an SD card, or you want to back up your iPhone. You would want to add some of these pictures to your collection. But you probably don't want to add all pictures.

picdedupe can help with these common problems:

- Do I already have this exact file?
- Do I even want to consider (accidental) screenshots?
- Do I have a better/worse version of this file? (e.g. RAW or .heic versus .jpg)
- Do I have a very similar picture? (e.g. same event, same place, same angle)
- ...

In addition, picdedupe is aware of common propoerties:

- Series that belong together (e.g. taken on the same day, at the same location)
- Files that represent 1 picture (e.g. RAW + .jpg, or .heic + .jpg)
- Files that represent a Live Photo (e.g. .mov + .jpg)
- ...

YOU choose! (indiviually, or set defaults)

- Should dupes be removed?
- Should .heic pictures replace .jpg versions?
- Should .mov files under 3 sec be removed if there is no .jpg to attach it to?
- Should RAW files be kept no matter what?
- ...

And much, much more!

- You can expand picdedupe with your own `Fixits`.
- Everything is modular; you could write another frontend.
- You can misuse it on purpose (e.g. as an indexer, or to find dupes within your collection)


**WARNING:** THIS IS NOT READY TO BE USED BY ANYONE.

**WARNING:** USE THIS AT YOUR OWN RISK (OF LOSING YOUR PICTURES)! MAKE BACKUPS!

