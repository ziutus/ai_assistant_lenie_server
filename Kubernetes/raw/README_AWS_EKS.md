## ekctrl installation

### Windows

```powershell
choco install -y eksctl
```

```powershell
choco upgrade -y eksctl
```

### cluster creation

```powershell
 eksctl create cluster --name stalker --version 1.29 --nodegroup-name workers1 --node-type t2.medium --nodes 1 --nodes-min 1 --nodes-max 4 --spot --vpc-nat-mode Disable --region us-west-1 --profile stalker-free-developer 
```

```powershell
eksctl delete cluster --name stalker --region us-west-1 --profile stalker-free-developer
```