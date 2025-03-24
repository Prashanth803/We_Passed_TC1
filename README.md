# We_Passed_TC1

Flow-
scenario - generate functioncalls -  process functioncalls -judge


log- all the code 
log1- generated function call
log2- function Declarations
api_mapping - maps api to fucntions
bdd.json -  all scenarios



/GitHub - 
logs all code in log.txt
generate function definitions in log2.txt
generate api mapping  in api_mapping.txt

/catfe/context - 
given the context generate bdd in bdd.json


/function - 
reads log1.txt (function calls) and read the api_mapping 
and call those apis - then judge func judges the result of those apis

/test - 
splits scenarios and call function that function calls for each scenario 


