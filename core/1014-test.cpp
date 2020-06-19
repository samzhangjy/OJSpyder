#include<iostream>
#include<cstdio>
using namespace std;
int main()
{
    int a;
    cin>>a;
    if (a>=90)
    {
    	cout<<"Excellent";
    }
    if (a>=80&&a<90)
    {
    	cout<<"Good";
    }
    if (a>=60&&a<80)
    {
    	cout<<"Pass";
    }
    if (a<60)
    {
    	cout<<"Fail";
    }
	return 0;
}