# Thoughts on content

Each page of a program contains an editable list of pagelets. Since it's really hard to have a nested, dynamic list of elements in the Django admin, the data is stored as JSON and rendered in the admin via a custom widget.

With PostgreSQL 9.3 or a NoSQL database like MongoDB, queries on this JSON may be possible, but as of now, it's really not needed.

## Text
Text is just text, and should use Markdown, preferably with a nice editor. 

    {
        "content_type": "text",
        "content": "This is a short piece of text using **Markdown**. It could be a lot longer."
    }

## Media
Media should come from Filer, as it's the best option for managing media in Django. However, we only need the filename reference to render. Each type of media is rendered it's own way.

    [
        {   
            "content_type": "image",
            "content": {
                "url": "filer/smoking_is_bad_mkay.jpg",
                "alt": "Smoking is bad",
                "title": "This image illustrates why smoking is bad",
            }
        },
        {   
            "content_type": "video",
            "content": {
                "url": "filer/like_really.mp4"
                // additional data
            }
        },
        {   
            "content_type": "audio",
            "content": {
                "url": "filer/motivational_speech.mp3"
                // additional data
            }
        },
        {   
            "content_type": "file",
            "content": {
                "url": "filer/infographic.pdf"
                // additional data
            }
        },
    ]

## Directive
Directives are a special case. The front end uses AngularJS. Something like a list that is collapsable by clicking a link will be rendered as a directive element, Angular will take care of the behaviour.

    {
        "content_type": "directive",
        "directive": "collapsable",
        "content": "- Cigarettes stink\n- You will live longer\n- Think of the children"
    }

## Form
Forms are the most complex ones.

    {
        "content_type": "form",
        "content": [
            {
                "field_type": "numeric",
                "variable_name": "NumberOfCigarettes",
                "label": "How many cigarettes do you smoke each day?",
                "required": False,
                "default": 0,
                "lower_limit": 0,
                "upper_limit": 200,
            },
            {
                "field_type": "string",
                "variable_name": "FirstWord",
                "label": "What's the first word that comes to your mind right now?",
                "required": False,
                "default": "",
            },
            {
                "field_type": "text",
                "variable_name": "Reason",
                "label": "Why, in your own words, do you want to quit smoking?",
                "required": False,
                "default": "",
            },
            {
                "field_type": "multiplechoice",
                "variable_name": "Reminder",
                "label": "Are you thinking about smoking right now?",
                "required": False,
                "default": "",
                "alternatives": [
                    {
                        "label": "That's a loaded question. You reminded me.",
                        "value": true
                    },
                    {
                        "label": "No. Never.",
                        "value": false
                    },
                ]
            },
            {
                "field_type": "multipleselection",
                "variable_name": "ReasonsChoice",
                "label": "Which of the following reasons are a good reason to quit?",
                "required": False,
                "default": "",
                "alternatives": [
                    {
                        "label": "Something",
                        "value": 1
                    },
                    {
                        "label": "Something else",
                        "value": 2
                    },
                    {
                        "label": "Something else entirely",
                        "value": 3
                    },
                ]
            },
        ]
    }
