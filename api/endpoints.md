| PATH                             | METHOD     | AUTHORIZATION       | DESCRIPTION                                                 |
| -------------------------------- | ---------- | ------------------- | ----------------------------------------------------------- |
| **/api/register/**               | **POST**   | **Public**          | Registers a user                                            |
| **/api/login/**                  | **POST**   | **Public**          | Logs in a user                                              |
| **/api/sentireader/**            | **GET**    | **Public**          | Demo endpoint for testing the model                         |
| **/api/journal-entries/**        | **GET**    | **Private** to user | Lists out all entries belonging to that user                |
| **/api/journal-entries/create/** | **POST**   | **Private** to user | Creates a new journal entry                                 |
| **/api/journal-entries/id/**     | **GET**    | **Private** to user | Return a single journal entry belonging to that user by ID  |
| **/api/journal-entries/id/**     | **PUT**    | **Private** to user | Updates a single journal entry belonging to that user by ID |
| **/api/journal-entries/id/**     | **DELETE** | **Private** to user | Deletes a journal entry belonging to that user by ID        |
| **/api/results**                 | **POST**   | **Private** to user | Return the results of a journal entry.                      |