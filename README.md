# picdedupe

This is very, very early work. It is probably **not useful** to you at this point.

Eventually, this will become two scripts, in Python, for macOS only:


## Script 1: Fingerprinting / Indexing

The first script will "fingerprint" a large number of pictures or movies.  
It does this by a combination of an MD5 hash and Spotlight metadata.  
It writes the result in a single images.json file.  
  
Consequetive runs over the same files should finish a lot quicker. As it uses
an existing images.json to detect changes. So it can skip work on unchanged
files.

If, however, you want to re-fingerprint everything, you can simply remove the
images.json file.


## Script 2: Detecting Dupes & Similar Images

Using the same images.json file (created by Script 1), it can check another 
folder structure of candidate images (e.g. new pics from your camera). 

If it finds a perfect dupe, it will drop the new file (by moving it into a
subfolder called ./_DUPES)

If it finds a very similar image, based on things like the resolution, the
GPS location, the camera, etc... it can act on that in several ways:

  - If it is a better version of the same image (e.g. an HEIC for a JPEG, or a   
    higher resolution version), it can replace the original (by renaming it,  
    e.g. filename.heic.jpg or filename_small.jpg, and moving it into a subfolder  
    called ./_SIMILAR as filename.heic.jpg)

  - If it is a worse version, it will leave the original and treat this one as   
    the lesser version in ./_SIMILAR

  - If it detects a movie of a picture (e.g. Apple's Live Photo), it will
    move the two together and name them appropriately (e.g. filename.jpg.mov).

  - If it detects a RAW of a .jpg, it will name it appropriately and put them  
    together as well.


WARNING: THIS IS NOT READY TO BE USED BY ANYONE.

WARNING: USE THIS AT YOUR OWN RISK (OF LOSING YOUR PICTURES)! MAKE BACKUPS!


