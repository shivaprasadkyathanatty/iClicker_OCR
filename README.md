**Instructions to run the code**:
1.Create folder "raw_images" in your local and Download raw ocr image files to the folder from "https://s3.console.aws.amazon.com/s3/buckets/ocr-raw-images?region=us-east-1&tab=objects"
2.Assign "raw_images" folder path to the variable "raw_image_path_folder"
3.Create folder "formatted_images" in your local and assign the folder path to the variable "formatted_image_path_folder"
4.Create folder "extracted_text" in your local and assign the folder path to the variable "text_file_path"
5.Create database "iclicker_ocr" in mysql
  mysql> create database iclicker_ocr;
6.Create a table named "iclicker" with fields file,question,optionA,optionB,optionC,optionD,optionE,optionF,optionG,optionH,low_confidence_score_count,high_confidence_score_count
  mysql> create table iclicker (file varchar(100),question BLOB,optionA BLOB,optionB BLOB,optionC BLOB,optionD BLOB,optionE BLOB,optionF BLOB,optionG BLOB,optionH BLOB,low_confidence_score_count int,high_confidence_score_count int);
7.Change user details at variable "config"
8.Run the code at terminal
9.View extracted text at mysql
  mysql> select file,convert(question using utf8),convert(optionA using utf8),convert(optionB using utf8),convert(optionC using utf8),convert(optionD using utf8),convert(optionE using utf8),convert(optionF using utf8),convert(optionG using utf8),convert(optionH using utf8) from iclicker_ocr.iclicker \G;
10.Export sql results to a csv file.
  $ mysql --user=root --password -B -e "select file,convert(question using utf8) as question,convert(optionA using utf8) as optionA,convert(optionB using utf8) as optionB,convert(optionC using utf8) as optionC,convert(optionD using utf8) as optionD,convert(optionE using utf8) as optionE,convert(optionF using utf8) as optionF,convert(optionG using utf8) as optionG,convert(optionH using utf8) as optionH from iclicker_ocr.iclicker" | sed "s/'/\'/;s/\t/\",\"/g;s/^/\"/;s/$/\"/;s/\n//g" > ocr_extracted_text_results.csv


