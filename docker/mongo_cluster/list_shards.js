const shards = db.adminCommand({ listShards: 1 }).shards;

shards.forEach(shard => {
  print(`Inspecting shard ${shard._id}`);

  const configDB = db.getSiblingDB('config');
  const collections = configDB.collections.find({ 'shard': shard._id }).toArray();

  collections.forEach(collection => {
    const dbName = collection._id.split('.')[0];
    const collName = collection._id.split('.')[1];
    const count = db.getSiblingDB(dbName).getCollection(collName).countDocuments();

    print(`  - ${collection._id}: ${count}`);
  });
});
