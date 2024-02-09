# MyYoutube Stage 5
A distributed video platform written using rpyc.  
To start, run `rpyc_registry`  
Then run `python monitor.py`  
Then run `python load_balancer.py`  
Then run `python name_service.py`  
Then run `python database.py`  
Then run `python application.py`  
Then run `python datanode.py` on each computer you want to host a datanode.  
You can run multiple datanodes in one computer if you clone the github repo in different folders.

Now open http://localhost:8080 on your browser.  

For how it works, please read the [Documentation](MyYoutube%20-%20Entrega%205.pdf)  
[Github Link](https://github.com/gustavomoura628/MyYoutube-Entrega5)  
![](screenshot_2.png)  
![](screenshot_1.png)  
![](screenshot_0.png)  
![](architecture.png)  
