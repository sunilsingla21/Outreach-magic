### Video
https://share.zight.com/Wnupk4Y6

#### Hosts table
-hosts are saved in an 'allHosts' array inside of the userSettings document for that username and password.<br>
-should be able to sort all tables and easily copy and paste text within them

##### Caclulate counts for each host in the array each time the loads
-calculating counts for each host<br>
```python total sent
collection: allEmailsUser
[
    {
        '$match': {
            'host': 'HOSTNAME'
        }
    }, {
        '$project': {
            'host': 1, 
            'sent': 1
        }
    }, {
        '$match': {
            'sent.filters.warmup': False, 
            'sent.filters.bounced': False
        }
    }, {
        '$unwind': {
            'path': '$sent'
        }
    }, {
        '$count': 'totalSent'
    }
]
```
```python total received
collection: allEmailsUser
[
    {
        '$match': {
            'host': 'HOSTNAME'
        }
    }, {
        '$project': {
            'host': 1, 
            'received': 1
        }
    }, {
        '$match': {
            'received.filters.warmup': False, 
            'received.filters.bounced': False
        }
    }, {
        '$unwind': {
            'path': '$received'
        }
    }, {
        '$count': 'totalReceived'
    }
]
```

```json
collection: userSettings
{
  "allHosts": [
    {
      "host": "outreachmagic",
      "hostCrypt": "outreachmagic_32d2",
      "counts":{
          "totalSent": 10323,
          "totalReceived":1323,
          "lastUpdated":{"$date":"timestamp"}
      }
    },
    {
      "host": "k2renewleads",
      "hostCrypt": "k2renewleads_2a352",
      "counts":{
          "totalSent": 10323,
          "totalReceived":1323,
          "lastUpdated":{"$date":"timestamp"}
      }
    },
    {
      "host": "operation",
      "hostCrypt": "operation_34da",
      "counts":{
          "totalSent": 10323,
          "totalReceived":1323,
          "lastUpdated":{"$date":"timestamp"}
      }
    }
  ]
}
```

#### Adding New Hosts
##### Check if host is avalaible
-first check if host is avalaible by seeing if any documents exist<br>
-user LOWER() for host

```python
collection: allEmailsUser
[
    {
        '$match': {
            'host': 'outreachmagic'
        }
    }, {
        '$count': 'documentCount'
    }
]
```

##### If any records are found
-print an error on the webApp 'host is already in use, add an existing host by using the hostCrypt or try a new host'

##### If no records are found 
###### calculate hostCrypt
-first calcuate the host crypt, we need a random hash<br>
-ideally would 5 character string<br>
-before I caclulated the host crypt in make like this: {{1.host}}_{{upper(substring(1.host; 1; 2))}}{{(length(1.host) * 3)}}{{upper(substring(1.host; 2; 3))}}<br>
-this turns outreachmagic into outreachmagic_U39T<br>
-and operationgraduate2 into operationgraduate2_P54E<br>
-you can use this same calculation or make a new one process if its better practice. It also does not have to include the 'host' in the hostCrypt.

###### add new array
-add to the userSettings collection allHosts array for that user<br>
-use LOWER() for host
```json
{
  "allHosts": [
    {
      "host": "outreachmagic",
      "hostCrypt": "outreachmagic_32d2",
      "counts":{
          "totalSent": 10323,
          "totalReceived":1323,
          "lastUpdated":{"$date":"timestamp"}
      }
    }
  ]
}
```

#### Adding Existing Hosts
-first see if the hostCrypt exists in the allEmailsUser database

```python
collection: allEmailsUser
[
    {
        '$match': {
            'userSettings.hostCrypt': 'hostCryptValue'
        }
    }, {
        '$count': 'documentCount'
    }
]
```
##### If no records are found
-print an error on the webApp 'hostCrypt is not found, please try again after some emails have been synced or add a new host'


##### If records are found
-add values to allHosts Array
```json
{
  "allHosts": [
    {
      "host": "outreachmagic",
      "hostCrypt": "outreachmagic_32d2",
      "counts":{
          "totalSent": 10323,
          "totalReceived":1323,
          "lastUpdated":{"$date":"timestamp"}
      }
    }
  ]
}
```


#### Deleting a host 
-delete array item for that host from the allHosts Array