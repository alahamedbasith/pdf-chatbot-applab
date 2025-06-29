## Test Report

The following table summarizes the results of executing the manual test cases described above.

| Test Case                                      | Status   | Notes                                              |
|------------------------------------------------|----------|----------------------------------------------------|
| 1. Verify Application is Running               | ✅ Pass  | Main UI loaded with "Upload PDF" and "Chat" sections. |
| 2. Successful PDF Upload                       | ✅ Pass  | PDF uploaded, success message and filename displayed. |
| 3. Uploading a Non-PDF File                    | ✅ Pass  | Error message shown: "Only PDF files are allowed." |
| 4. Re-uploading an Existing PDF                | ✅ Pass  | Error message shown: document already uploaded.    |
| 5. Chat with a Document (Relevant Question)    | ✅ Pass  | Chatbot answered accurately from PDF content.      |
| 6. Chat with a Document (Irrelevant Question)  | ✅ Pass  | Chatbot responded: "Sorry, I couldn't find anything related." |
| 7. Verify Ollama Service Health Check          | ✅ Pass  | JSON response: `{"status":"ok"}` displayed.        |

All test cases passed as expected. The PDF Chatbot application is functioning correctly based on the manual tests performed.
