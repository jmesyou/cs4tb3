# compile the grammar and put the generated source into the parser package
java -cp antlr-4.6-complete.jar org.antlr.v4.Tool -o src/cas/cs4tb3/parser -no-listener MIDee.g4

# create a directory for the output
mkdir build

# compile the source which includes the generated files from antlr
javac -cp "antlr-4.6-complete.jar" -d build -sourcepath src src/cas/cs4tb3/MIDee.java

# bundle the compiled classes into a jar
jar cfm MIDee.jar src/META-INF/MANIFEST.MF -C build .
