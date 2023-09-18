#!/usr/bin/python

import os
import sys
import ldap
import getpass
import traceback
import pprint




def main():    
    SERVER = 'ldap://authldap.gwu.edu:389'
    DN = 'ou=people,dc=gwu,dc=edu'
    user = "uid=%s,ou=people,dc=gwu,dc=edu" 
    passwd = None
    uid = None    

    try:
        uid = raw_input("Please enter your netid: ")
        user = user % uid
        passwd = getpass.getpass("Please enter your ldap password: ")
	
        
        gwidFile = sys.argv[1]
        f = open(gwidFile, "r")
        l = ldap.initialize(SERVER)
        l.simple_bind_s(user, passwd)
        
        print "GWID,\t\tNetID,\t\tLastName,\t\tFirstName,\tEmail,\tStatus,\tisFaculty,\tisStaff,\tisWage,\tisStudent,\tisAlum"
        for gwid in f:
            searchFilter = "GWid=%s" % gwid
	    rIndex = l.search(DN, ldap.SCOPE_SUBTREE, searchFilter, ["GWid", "uid", "sn", "givenName", "mail", "gwStatus", "GWaccType"])
            result_type, result_data = l.result(rIndex)
	    if (result_data == []):
		print "Error getting data for filter=%s" % searchFilter
		continue            
            
            result = result_data[0][1]
	    
	    #set the values for the account type
	    account_types = result['GWaccType']
	    isStaff = False
	    isFac = False
	    isStudent = False
	    isAlum = False
	    isWage = False
	    isAffiliate = False
	    

	    for aType in account_types:
		if aType.find("staff") >= 0:
		    isStaff = True
		
		elif aType.find("faculty") >= 0:
		    isFac = True
		
		elif aType.find("student") >= 0:
		    isStudent = True
		    
		elif aType.find("alumni") >= 0:
		    isAlum = True
		
		elif aType.find("wage") >= 0:
		    isWage = True
		    
		else:
		    print "UNKNOWN ACCOUNT TYPE: %s" % aType.strip()
	    
	    
	    print "%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t%s,\t%s" % (result['GWid'][0].strip(), result['uid'][0].strip(), result['sn'][0].strip(), result['givenName'][0].strip(), result['mail'][0].strip(),result['gwStatus'][0].strip(), isFac, isStaff, isWage, isStudent, isAlum)
   
    except getpass.GetPassWarning:
        print "meh"
        
    except:
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)
        


if __name__=="__main__":
    main()