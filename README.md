# MyYoutube Stage 2
A distributed video platform written using only sockets.  
To start, run `python application.py`  
Then run `python database.py`  
Then run `python datanode.py` on each computer you want to host a datanode.  
If you want, you can run multiple datanodes in one computer by changing the port number on datanode.py  
After starting all datanodes, add their ip and port to datanodes.txt in the computer running the application  

Now open http://localhost:8080 on your browser.  

![](screenshot_2.png)  
![](screenshot_1.png)  
![](screenshot_0.png)  
