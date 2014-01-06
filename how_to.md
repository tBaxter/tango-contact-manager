##PContact Manager
Allows for fast and easy creation of user information for contact forms, "send us your story", simple photo submissions, or pretty much anything else we might want users to submit.

####Creating a Form

1. Basic fields
    - Give your form a name
    - **Request contact info** collects an address and phone number. You should not use this unless you <i>desperately</i> require this information. People don't like giving our their address when they don't think you need to know it.  
    - **Allow uploads** lets the submitter add a photo to their submission. Leave it unchecked unless you have a plan for the photos.  
    - **Limit Words** caps submissions to the number of words you allow. In many cases, you might not want to let people ramble. If you don't care how long the submissions are, leave it blank.  
    - **Override subject** provides a default subject for submissions. If left blank, the submitter will write their own.  
    - **Subject label** Allows for customizing the subject field label. By default, it is "Subject". If you would like the label to read something else, such as "Headline", enter it here. Note: if you put anything in the "Override Subject" field, the subject is not shown.  
    - **Body label** Allows for customizing the body field label. By default, it is "Your message". If you would like the label to read something else, such as "Body", enter it here.  
    - Optionally, you can create a custom introductory message and thank you message. In most cases, you won't need or want to. The defaults will work and display well.  
2. Routing
    - **Store to DB:** Use when you intend to use/publish submissions, or would like to create a permanent record  
    - **Send emails:** Instead of storing responses in the database, they are immediately forwarded. Be sure to set the email options and recipients - **Email Options:** Determines whether emails should be sent to everyone in the recipients list, or if the user should be presented with a list of possible recipients from which to choose. Note: If you only have one recipient -- or if the recipient is an email distribution group -- don't make the user select it from a list.       
    - If the message needs to be emailed (probably, just so someone knows we got it) you can select the people you want it sent to. If you don't see your intended recipient, use the green add button next to **Other Recipients** to create a new one. Common uses may be "Technical Help" or "Web Editors," who aren't users in the system.  
3. Admin fields (collapsed by default)
    - Site defines which site the form belongs to.  
    - Slug is the form slug. Used for URLs, among other things.  
    - "Request assignment to section" prompts the submitter to select a section. Useful for when the entries will be published, as on Press Release Central.  
    - "Require sign-in" requires the user to sign in before they can fill out and submit the form.  

####Stored Submissions
1. Go to "Submitted Content." These are your received messages.  
2. On the sidebar, you can filter by the form you want responses from.  
3. In the contact, you can access all the information they sent.  
4. There are two checkboxes that interest you:
    - **Exported** This notes if a message has been exported to a document to be used in print. Letters to the Editor uses this to keep track of what they're done with.  
    - **Publish** Used for a "Share your stories" type feature. If you have a section of this on your site, you need to read and possibly edit (removing personal contact info from the body, etc.) the submissions before checking publish. This will cause it to appear on the site.  
