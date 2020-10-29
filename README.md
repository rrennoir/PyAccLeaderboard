# PyAcc_leaderboard

![app](./images/app.png)

## Version 0.4

* Major GUI redesing
* Add a font that doesn't looks like shit :joy:
* Clear GUI when entry list update is reveiced
* Fix bug when data send by the acc thread isn't complete during entry list update
* Fixed broken read_f32() function returning garbage value
* Add session information (time left, cloud cover, rain level, temps, ect) to app screen
* Add cute emoji to indicate car location (in pit or track)
* Changed some header title
* Updated accProtocol to get session information
* Plus other stuff that I already forgot ...

## Version 0.3

* Handle error and timeout, now even if the game is closed or the session is over the app **shouldn't** crash and wait to reconnect
* ACC worker thread handle socket stuff by itself
* Add window title (***very important***)
* Make print message cutier or uglier :grimacing:
* Added some comment may be if I'm not too lazy the code will be commented :joy:
* Make the first letter uppercase in the previous patch note because uppercase life matters :neckbeard:
* EMOJI EVERYWHERE !!! :smiling_imp: :blush:

## Version 0.2.1

* Added command line args for ip and port => `python main.py [ip] [port]`, no args will use localhost and port 9000

## Version 0.2

* I still don't know what I'm doing with threads, but it should :tm: be better
* Bug fixes
* Fixed bug added by the bug fix
* New GUI theme to make the eyes suffer less
* Removed nords for sanity

## Version 0.1

* Idk what I'm doing with thread, plz don't @me
* It might dead lock
* It might crash the game (:
* At least the basic work
* Added nords <3
