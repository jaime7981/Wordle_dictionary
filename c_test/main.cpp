#include <stdio.h>
#include <curl/curl.h>
#include <string>

using namespace std;

int main(void)
{
    CURL *curl = curl_easy_init();
    if(curl) {
        const char *data = "submit = 1";

        curl_easy_setopt(curl, CURLOPT_URL, "http://10.5.10.200/website/WebFrontend/backend/posttest.php");

        /* size of the POST data */
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, 10L);

        /* pass in a pointer to the data - libcurl will not copy */
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);

        curl_easy_perform(curl);
    }
    /* Perform the request, res will get the return code */ 
    /* always cleanup */ 
    return 0;
}