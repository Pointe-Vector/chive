# Overview
Chive keeps your digital archive safe. It is a tool for establishing and checking file integrity. It is not a security product.

# Requirements
Chive only requires Python 3.11. There are no external dependencies!

# Architecture
A manifest is maintained of the files protected by a Chive archive in the form of a SQLite database. It contains a merkle-tree-like hash of each file by relative path from the manifest. Utilities are provided as a command-line interface to:
- (init) Initialize a file
- (list) List files in the manifest
- (append) Add a file to the manifest
- (remove) Remove a file from the manifest
- (check) Ensure a file in the manifest has not changed
- (verify) Ensure two manifests are equivalent
- (repair) TODO! Fix errors in a file

# Why Chive Was Made
I need to store many large files for decades. These files are highly valuable but not mission-critical. Two copies of each file and the associated manifest are stored on geographically separated harddrives that are offline. A third copy of the manifest is stored in the cloud. Chive helps me create these manifests, ensure files are copied correctly, and validate the integrity of the offine files. If errors are found, the consensus between the three manifests directs which chunks from each copy of the file are correct.

# Solutions That Are Probably Better For You
- ZFS for Linux environments
- 3-2-1 for mission critial data