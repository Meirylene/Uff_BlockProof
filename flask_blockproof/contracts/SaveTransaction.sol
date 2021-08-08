pragma solidity >=0.4.22 <0.8.0;

contract SaveTransaction {
    
   
    struct Transaction {
        string urlHash;
        string[] contentHash;
        string[] contentHash2;
        string[] minList_minHash1;
        string[] minList_minHash2;
        string[] jaccard; 
        string[] user;
        uint contContent;
        address[] msender;
        string[] time;
        string[] title; 
        
    }

  mapping (string => Transaction) registros;
  
//1) Store the values in the struct.
//2) Store the structure in the mapping.
//3) Append the primary key to the index array. This forms an unordered list of the keys in the system.

function insertTransaction(string memory urlHash, string memory contentHash,string memory contentHash2 ,string memory user, string memory time, string memory title, string memory minList_minHash1,string memory minList_minHash2 ,string memory jaccard)  public returns(bool success) {
    
    if(registros[urlHash].contContent == 0){ // primeiro registro
    
    registros[urlHash].urlHash = urlHash;
    registros[urlHash].user.push(user);
    registros[urlHash].contentHash.push(contentHash);
    registros[urlHash].contentHash2.push(contentHash2);
    registros[urlHash].minList_minHash1.push(minList_minHash1);
    registros[urlHash].minList_minHash2.push(minList_minHash2);
    registros[urlHash].jaccard.push(jaccard);
    registros[urlHash].contContent = registros[urlHash].contentHash.length; //a contagem começa de zero
    registros[urlHash].msender.push(msg.sender);
    registros[urlHash].time.push(time);
    registros[urlHash].title.push(title);
    
    return true;
        
    }else{
        
         if (compareStrings(registros[urlHash].contentHash[registros[urlHash].contentHash.length-1],contentHash) ){
          return false;
         }         
    
         registros[urlHash].urlHash = urlHash;
         registros[urlHash].user.push(user);
         registros[urlHash].contentHash.push(contentHash);
         registros[urlHash].contentHash2.push(contentHash2);
         registros[urlHash].minList_minHash1.push(minList_minHash1);
         registros[urlHash].minList_minHash2.push(minList_minHash2);
         registros[urlHash].jaccard.push(jaccard);
         registros[urlHash].contContent = registros[urlHash].contentHash.length; //a contagem começa de zero
         registros[urlHash].msender.push(msg.sender);
         registros[urlHash].time.push(time);
         registros[urlHash].title.push(title);
       
         return true;

  }

}


function compareStrings(string memory a, string memory b) pure internal returns (bool) { 
    return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
}

function qtdRegContent(string memory urlHash) public view returns (uint qtd) { 
    return (registros[urlHash].contContent) ;
}

function consulta_urlHash (string memory _urlHash) public view returns (string memory urlHash){
     return (registros[_urlHash].urlHash);
}  

function consulta_minList_minHash1 (string memory _urlHash,uint pos) public view returns (string memory minList_minHash1){
     return (registros[_urlHash].minList_minHash1[pos]);
}  

function consulta_minList_minHash2 (string memory _urlHash,uint pos) public view returns (string memory minList_minHash2){
     return (registros[_urlHash].minList_minHash2[pos]);
} 

function consulta_jaccard (string memory _urlHash,uint pos) public view returns (string memory jaccard){
     return (registros[_urlHash].jaccard[pos]);
}  

function consulta_ContentHash(string memory _urlHash,uint pos) public view returns (string memory contentHash){
     return (registros[_urlHash].contentHash[pos]);
}

function consulta_ContentHash_2(string memory _urlHash,uint pos) public view returns (string memory contentHash2){
     return (registros[_urlHash].contentHash2[pos]);
}

function consulta_user (string memory _urlHash,uint pos) public view returns (string  memory user){
     return (registros[_urlHash].user[pos]);
}  

function consulta_sender (string memory _urlHash,uint pos) public view returns (address sender){
     return (registros[_urlHash].msender[pos]);
}  

function consulta_time(string memory _urlHash,uint pos) public view returns (string memory time){
     return (registros[_urlHash].time[pos]);
}  

function consulta_title(string memory _urlHash,uint pos) public view returns (string memory title){
     return (registros[_urlHash].title[pos]);
}  

}
