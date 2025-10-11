This project consist of MCP server tooling that allows one to use Claude code as a scripture study tool.  It includes the following:
- an expandable index that includes at a minimum the KJV Old Testament, KJV New Testmanet, Book of Mormon, Doctrine and Covenants, Pearl of Great Price
- an MCP server for querying the scriptures that includes the following endpoints:
  1. fetch a scripture reference from a natural language query (e.g., "1 ne 3:7-8") which looks up and returns two verses in standard format. This requires a plaintext reference parser
  2. exact search for a string across all scriptures, returning the verse and a phrase in context (JSON)
  3. semantic search for a string across al scriptures using a vector database, returning the verse and a phrase in context (JSON). [for this it might be useful to use a timy embedding model https://huggingface.co/NeuML/colbert-muvera-nano with only 970K params]

Plain Text Reference Parser
The plain text reference parser does it's best to take plain text strings like "Alma1-2;4-5:10;jas1:5-6" and return a programmatical response of the selected books, chapters, and verses. Which response can then be used to query for those selected books if desired.

GET /referencesParser
Required query parameters
Name
reference
Type
string
Description
The string that should be parsed

Name
api-key
Type
string
Description
The API Key associated with your account. Learn more at API Keys

Response
Name
references
Type
array
Description
An array of book objects that were referenced in the reference string

Name
references[].book
Type
array
Description
The book id of the referenced book. This id can be used to obtain the book via the books endpoint

Name
references[].chapters
Type
array
Description
An array of chapter objects, which are the chapters referenced within the given book

Name
references[].chapters[].start
Type
number
Description
The starting chapter for this chapter segment

Name
references[].chapters[].end
Type
number
Description
The ending chapter for this chapter segment. Note: If only one chapter was referenced for this chapter segment, then the start and end values will be the same

Name
references[].chapters[].verses
Type
array
Description
An array of verse segments which were referenced for the end chapter. If no verses were referenced than this array will be empty

Name
references[].chapters[].verses[].start
Type
number
Description
The starting verse for this verse segment

Name
references[].chapters[].verses[].end
Type
number
Description
The ending verse for this verse segment. Note: If only one verse was referenced for this verse segment, then the start and end values will be the same

Name
prettyString
Type
string
Description
A standardized string of the provided references, with correct spacing, etc.

Name
valid
Type
boolean
Description
A boolean value of whether the provide reference string was able to be parsed. If false an error attribute will be provided with details as to why the reference string couldn't be parsed

Name
error
Type
string
Description
If the valid attribute is false, this will be an error string of why the reference couldn't be parsed

Example response:
Response for "Alma1-2;4-5:10;jas1:5-6"
{
  "references": [
    {
      "book": "alma",
      "chapters": [
        {
          "start": 1,
          "end": 2,
          "verses": []
        },
        {
          "start": 4,
          "end": 5,
          "verses": [
            {
              "start": 10,
              "end": 10
            }
          ]
        }
      ]
    },
    {
      "book": "james",
      "chapters": [
        {
          "start": 1,
          "end": 1,
          "verses": [
            {
              "start": 5,
              "end": 6
            }
          ]
        }
      ]
    }
  ],
  "prettyString": "Alma 1-2; 4:5-19; James 1:5-6",
  "valid": true
}


{
  "volumes": [
    {
      "_id": "oldtestament",
      "title": "Old Testament"
    },
    {
      "_id": "newtestament",
      "title": "New Testament"
    },
    {
      "_id": "bookofmormon",
      "title": "Book of Mormon"
    },
    {
      "_id": "doctrineandcovenants",
      "title": "Doctrine and Covenants"
    },
    {
      "_id": "pearlofgreatprice",
      "title": "Pearl of Great Price"
    }
  ]
}


{
  "_id": "1nephi",
  "title": "1 Nephi",
  "titleShort": "1 Ne",
  "titleOfficial": "THE FIRST BOOK OF NEPHI",
  "subtitle": "HIS REIGN AND MINISTRY",
  "summary": "An account of Lehi and his wife Sariah, and his four sons, being called, (beginning at the eldest) Laman, Lemuel, Sam, and Nephi. ....  This is according to the account of Nephi; or in other words, I, Nephi, wrote this record.",
  "chapterDelineation": "Chapter",
  "chapters": [
    {
      "_id": "1nephi1",
      "summary": "Nephi begins the record of his people—Lehi sees in vision a pillar of fire and reads from a book of prophecy—He praises God, foretells the coming of the Messiah, and prophesies the destruction of Jerusalem—He is persecuted by the Jews. About 600 B.C."
    },
    {
      "_id": "1nephi2",
      "summary": "Lehi takes his family into the wilderness by the Red Sea—They leave their property—Lehi offers a sacrifice to the Lord and teaches his sons to keep the commandments—Laman and Lemuel murmur against their father—Nephi is obedient and prays in faith; the Lord speaks to him, and he is chosen to rule over his brethren. About 600 B.C."
    },
    //...
    {
      "_id": "1nephi22",
      "summary": "Israel will be scattered upon all the face of the earth—The Gentiles will nurse and nourish Israel with the gospel in the last days—Israel will be gathered and saved, and the wicked will burn as stubble—The kingdom of the devil will be destroyed, and Satan will be bound. About 588–570 B.C."
    }
  ]
}


{
  "_id": "1nephi1",
  "nextChapterId": "1nephi2",
  "prevChapterId": "revelation22",
  "volume": {
    "title": "Book of Mormon",
    "titleShort": "BoM",
    "titleOfficial": "The Book of Mormon",
    "_id": "bookofmormon"
  },
  "book": {
    "title": "1 Nephi",
    "titleShort": "1 Ne",
    "titleOfficial": "THE FIRST BOOK OF NEPHI",
    "subtitle": "HIS REIGN AND MINISTRY",
    "summary": "An account of Lehi an ..., I, Nephi, wrote this record.",
    "_id": "1nephi"
  },
  "chapter": {
    "bookTitle": "1 Nephi",
    "delineation": "Chapter",
    "number": 1,
    "summary": "Nephi begins the record of ... He is persecuted by the Jews. About 600 B.C.",
    "chapterAugmentations": [],
    "verses": [
      {
        "text": "I, Nephi, having been born of goodly parents, ...  in my days.",
        "footNotes": [],
        "italics": [],
        "associatedContent": []
      },
      {
        "text": "Yea, I make a record in the language of my father, which consists of the learning of the Jews and the language of the Egyptians.",
        "footNotes": [],
        "italics": [],
        "associatedContent": []
      },
        // ...
      {
        "text": "And when the Jews ... of deliverance.",
        "footNotes": [],
        "italics": [],
        "associatedContent": []
      }
    ]
  }
}

