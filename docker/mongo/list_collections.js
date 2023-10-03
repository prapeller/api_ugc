db.adminCommand({ listDatabases: 1 }).databases.forEach(function(dbInfo) {
  var db = new Mongo().getDB(dbInfo.name);
  print("Database: " + dbInfo.name);
  db.getCollectionNames().forEach(function(collName) {
    print("  - " + collName + ": " + db.getCollection(collName).countDocuments());
  });
});
