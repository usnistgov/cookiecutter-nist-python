p=$(PWD)

cd $p/docs-nist-pages/html


for x in *; do
    if [ $x = 'src' ] ; then
        echo "$x is src. continue"
        continue

    elif [[ $x == *.sh ]] ; then
        echo "$x is bash. continue"
        continue

    elif [ $x == ".git" ] ; then
        echo "$x is git. continue"
        continue

    else
        rm -rf $x

    if
done
