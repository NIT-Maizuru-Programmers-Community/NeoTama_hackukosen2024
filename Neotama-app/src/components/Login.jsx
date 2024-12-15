import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "@/lib/firebase";

const Login = () => {
	const Googlerovider = new GoogleAuthProvider();
	const signInWithGoogle = () => {
		signInWithPopup(auth, Googlerovider);
	};
	return (
		<div className='h-screen  items-center justify-center flex'>
			<Card className='w-full mx-3 py-10 my-5'>
				<CardHeader>
					<CardTitle className='text-center text-3xl'>ログイン</CardTitle>
				</CardHeader>
				<CardContent className='text-center space-y-2'>
					<Button className='w-full mx-2' onClick={signInWithGoogle}>
						Googleでログイン
					</Button>
				</CardContent>
			</Card>
		</div>
	);
};

export default Login;
