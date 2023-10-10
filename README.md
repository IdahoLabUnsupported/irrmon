# irrmon
This software gathers irrigation data as well as evapotranspiration rates to understand the on field water balances and track water usage.

## Notice to potential users
This software was built to meet the specific needs a single farm on a relatively short time frame. Due to these requirements, the flexability to handle a variety of data sources and use cases has not been provided for or implemented. This
code is not being actively maintained and no improvements are planned.

### User Requirements
This software was built to utilize an api that was provided by PivotTrac and requires that the "groupID" is entered as a string in the config.json file. If a different api is being used it is likely that line 16 in update.py will need
to be updated to point to the correct locations. Similarly this software was built to utilize AGRIMET data from the Northwest U.S. if you have another source of ET and precipiation data you will need to update lines 49 and 71 in update.py 
respectively.  However, the author cannot gurantee that formats of other data sources will be usable in this code as written.


