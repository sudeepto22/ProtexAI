#!/bin/bash

echo "===================="
echo "ProtexAI Metrics DB"
echo "===================="
echo ""

# Total count
echo "Total metrics stored:"
docker exec mongodb mongosh --quiet --username protexai --password protexai123 \
  --eval "db.getSiblingDB('protexai').metrics.countDocuments()"

echo ""
echo "Latest 5 metrics:"
docker exec mongodb mongosh --quiet --username protexai --password protexai123 \
  --eval "
    db = db.getSiblingDB('protexai');
    db.metrics.find()
      .sort({timestamp: -1})
      .limit(5)
      .forEach(doc => {
        print('---');
        print('Time:', doc.timestamp);
        print('CPU:', doc.cpu.usage_percent + '%');
        print('GPU:', doc.gpu.map(g => g.name + ' (' + g.load_percent + '%)').join(', '));
        print('Temperature:', doc.temperature.map(t => t.name + ': ' + t.temperature_c + '°C').join(', '));
        print('RAM:', doc.ram.used_gb + 'GB /' , doc.ram.total_gb + 'GB (' + doc.ram.usage_percent + '%)');
        print('Disk:', doc.disk.used_gb + 'GB /' , doc.disk.total_gb + 'GB (' + doc.disk.usage_percent + '%)');
      })
  "

echo ""
echo "Average CPU and RAM usage:"
docker exec mongodb mongosh --quiet \
  --username protexai --password protexai123 \
  --eval "
    db = db.getSiblingDB('protexai');
    db.metrics.aggregate([
      { \$group: {
          _id: null,
          avgCPU: { \$avg: '\$cpu.usage_percent' },
          avgRAM: { \$avg: '\$ram.usage_percent' }
        }
      }
    ])
    .forEach(result => {
      print('Average CPU:', result.avgCPU);
      print('Average RAM:', result.avgRAM);
    })
  "

