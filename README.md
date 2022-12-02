# ClusterEFF
GUI-Based messaging Application

Instructions:

    To do a localhost trial:
        1. Open server.py and leave it running
        2. Open client.py
        3. Enter Display Name
    Client will automatically connect to the server

    To host over a network:

    IMPORTANT NOTES: When linking clients over the network, every client, and the server device, will need a copy of SETTINGS.txt, this is how the clients and the server get their connection details
        
        1. Change the ip address in SETTINGS.txt on the server.py computer to the IP address of that device
        2. Make sure to that every client's SETTING.txt file is updated with the new IP address
        3. Open server.py and leave it running
        4. Run client.py like normal on every device thats connecting, and the clients will connect automatically

    If you are connecting clients from outside of your local network, you'll need to forward the appropriate port(40000 by default), and set the IP address in the SETTINGS.txt file for server.py to the public IP address for the device

   If you have an questions about these instructions, please reach out the coby.kuhns@gmail.com. I'm always happy to help out :)   
