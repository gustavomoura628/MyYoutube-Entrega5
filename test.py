hosts_data = {"host1:address": {"number_of_files": 10},
"host2:address": {"number_of_files": 15},
"host3:address": {"number_of_files": 1},
"host4:address": {"number_of_files": 0}}

sorted_addresses = sorted(hosts_data.keys(), key=lambda x: hosts_data[x]['number_of_files'])

# Print the sorted addresses
for address in sorted_addresses:
    print(f"Address: {address}, Number of Files: {hosts_data[address]['number_of_files']}")

