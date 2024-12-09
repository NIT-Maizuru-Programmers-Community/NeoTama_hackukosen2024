import React from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "@/lib/firebase";
import { Button } from "./ui/button";
import { Link } from "react-router-dom";
import { signOut } from "firebase/auth";

const Home = () => {
	const [user] = useAuthState(auth);
	return (
		<div className='min-h-screen flex flex-col bg-gray-50'>
			<header className=' shadow-sm text-black text-2xl font-bold p-4 flex justify-between items-center'>
				<h1>ネオたま</h1>
				<div className='flex space-x-3'>
					{user && (
						<img
							src={user.photoURL}
							alt={user.displayName}
							className='w-10 h-10 rounded-full'
						/>
					)}
					{user ? (
						<Button onClick={() => signOut(auth)}>Logout</Button>
					) : (
						<Button>
							<Link to='/login'>Login</Link>
						</Button>
					)}
				</div>
			</header>
			<main className='flex flex-col items-center gap-6 p-4 flex-grow'>
				<div className=''>
					<img
						src='/IMG_20241016_154131.jpg'
						alt='サンプル写真'
						className=' flex flex-col items-center gap-6 p-4 flex-grow'
					/>
					<img
						src='/IMG_20241016_154131.jpg'
						alt='サンプル写真'
						className=' flex flex-col items-center gap-6 p-4 flex-grow'
					/>
				</div>
			</main>
			<div className='fixed bottom-2 right-2 rounded-full text-center ring-offset-blue'>
				<Button className='w-15 h-15 rounded-full'>
					<Link to='/add' className='text-2xl'>
						+
					</Link>
				</Button>
			</div>
		</div>
	);
};

export default Home;
