## 📦 TFHCLUpdate
A Python CLI tool to Get/Update variables in Terraform .tf files.

### 🚀 Features
✅ Retrieve variable values from Terraform variables.tf files

✅ Update string variables, maps, or nested values

✅ Easily integrate with Jenkins Shared Libraries for automation

### 🛠️ Installation
Make sure you have Python 3+ installed. Then install the required dependencies:

```shell
pip install -r requirements.txt
```

### 📌 Usage
#### 🔄 Replace a string variable
```sh
python main.py --file variables.tf --variable vpc_cidr_block --data '10.0.0.0/24'
```

#### 🔄 Replace a map variable
```sh
python main.py --file variables.tf --variable tags --data "{'Owner': 'prod-team', 'Environment': 'prod'}"
```

#### ➕ Add an entry to a map
```sh
python main.py --file variables.tf --variable tags --data "{'Owner': 'prod-team', 'Environment': 'prod', 'Region': 'eu-west'}"
```

### ⚙️ Jenkins Shared Library Integration
You can integrate this tool into your Jenkins shared libraries to automate Terraform updates.

#### 🗂️ Groovy Script (Place in Shared Library)
```
import groovy.json.JsonSlurperClassic
import groovy.json.JsonOutput

@NonCPS
def jsonParse(def json) {
    new JsonSlurperClassic().parseText(json)
}

def get_variable(file_name="", variable="") {
    def content = libraryResource 'tf_replace.py'
    writeFile file: 'main.py', text: content

    def result = sh(returnStdout: true, script: "python main.py --file ${file_name} --variable ${variable}")

    try { 
        return jsonParse(result)
    } catch(Exception ex) {
        return result
    }
}

def set_variable(file_name="", variable="", data="") {
    script {
        def content = libraryResource 'tf_replace.py'
        writeFile file: 'main.py', text: content

        try { 
            data = JsonOutput.toJson(data).replace('"', "'")
        } catch(Exception ex) {
            if (data instanceof String) {
                data = "'${data}'"
            }
        }

        def result = sh(returnStdout: true, script: """python main.py --file ${file_name} --variable ${variable} --data "${data}" """)
        return result
    }
}
```

#### 🧪 Jenkins Declarative Pipeline Usage
```
stage('Update Terraform Tags') {
    steps {
        script {
            def tags = tf_replace.get_variable("variables.tf", "tags")
            tags.Region = "eu-west"
            tf_replace.set_variable("variables.tf", "tags", tags)
        }
    }
}
```

### 📁 Project Structure
```
.
├── main.py           # Your CLI script
├── variables.tf      # Example Terraform file
├── README.md         # Readme file
└── requirements.txt  # Dependencies
```

### 🙌 Contributing
Feel free to open issues or PRs! Feedback and contributions are welcome.