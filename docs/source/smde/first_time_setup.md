# First time setup

If you believe you need access to the SMCE HPC SLURM cluster, contact Greg Olmschenk on the RGES-PIT Slack, and we'll decide if this is the appropriate route for you. If this has already been determined, proceed with the below.

## SSH access

Next, you will need to send an SSH public key to the Roman Project Computing Infrastructure Team so that they can set up an account you can log into. First, generate a new SSH key public/private pair. On macOS and Linux, from the terminal, run
```sh
ssh-keygen -t ed25519 -f ~/.ssh/roman_smdc
```
and follow the prompts. This will create two files, the private key `~/.ssh/roman_smdc` and the public key `~/.ssh/roman_smdc.pub`. Never share the private key with anyone. Note, the HPC SLURM cluster does not require a NASA account or VPN to access. They prefer to register the account with your NASA email if you have one, but, even if they do, you do not need to use the NASA account or VPN to log in. Now, send the following items to Greg Olmschenk:
1. Your preferred username.
2. The email to associate with the account (if you have a NASA email they prefer that).
3. The public SSH key you generated.
Next, you need to wait for Roman infrastructure team to set up your account.

Once you have received confirmation from that your HPC SLURM cluster account has been created, add the following to your SSH configuration file (located at `~/.ssh/config` on macOS and Linux). Replace `{your_user_name}` with the username you received.
```
Host roman_smdc
    HostName hpc-east-1.roman.sciencecloud.nasa.gov
    User {your_user_name}
    IdentityFile ~/.ssh/roman_smdc
```

Now, you should be able to SSH into the HPC SLURM cluster with
```
ssh roman_smdc
```
