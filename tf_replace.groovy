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