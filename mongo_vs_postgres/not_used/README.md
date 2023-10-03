instead of storing in 2 different collections:

```
"film_comments": [
    {
      "film_uuid": "uuid",
      "film_comments": [
        {
          "comment_uuid": "uuid",
          "created_at": "timestamp",
          "updated_at": "timestamp",
          "user_uuid": "uuid",
          "comment": "string"
        }
      ]
    }
  ],
    "film_avg_ratings": [
    {
      "film_uuid": "uuid",
      "avg_rating": "float"
    }
]
```

probably better to store in single collection
```
"film_comments_ratings": [
      {
        "film_uuid": "uuid",
        "avg_rating": "float",
        "film_comments": [
          {
            "comment_uuid": "uuid",
            "created_at": "timestamp",
            "updated_at": "timestamp",
            "user_uuid": "uuid",
            "comment": "string"
          }
        ]
      }
    ]
```
but... while etl from postgres - query (described in generate_fake_data2.py) consumed to much storage.
that's why decided to devide into 2 collections