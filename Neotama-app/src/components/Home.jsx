import React, { useEffect } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useState } from "react";
import { auth, db } from "@/lib/firebase";
import { Button } from "./ui/button";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { collection, getDocs } from "firebase/firestore";
import { Plus, UserPlus } from "lucide-react";
import {
	Card,
	CardHeader,
	CardTitle,
	CardContent,
	CardFooter,
} from "./ui/card";

const Home = () => {
	const [user] = useAuthState(auth);
	const [allDatas, setAllDatas] = useState([]);
	const navigate = useNavigate();
	const getAllDatas = async () => {
		const querySnapshot = await getDocs(
			collection(db, "Users", user.uid, "Collections")
		);
		const allDatas = querySnapshot.docs.map((doc) => {
			const docData = doc.data();
			docData.time_stamp = docData.time_stamp.toDate();
			return docData;
		});
		allDatas.sort((a, b) => b.time_stamp - a.time_stamp);
		allDatas.forEach((data) => {
			data.time_stamp = data.time_stamp.toLocaleString();
		});
		setAllDatas(allDatas);
		console.log(allDatas);
	};
	useEffect(() => {
		if (user) {
			getAllDatas();
		}
	}, [user]);
	const handleSignOut = () => {
		signOut(auth);
		navigate("/login");
	};
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
						<Button onClick={handleSignOut}>Logout</Button>
					) : (
						<Button>
							<Link to='/login'>Login</Link>
						</Button>
					)}
				</div>
			</header>
			<main className='flex flex-col items-center gap-6 p-4 flex-grow'>
				{allDatas.length === 0 && <p>データがありません</p>}
				{allDatas &&
					allDatas.map((data, index) => (
						<Card key={index} className='w-full'>
							<CardHeader>
								<CardTitle className='text-center'>
									渡した相手：{data.name}
								</CardTitle>
							</CardHeader>
							<CardContent className='text-center'>
								<img src={data.url} alt={data.title} className='w-full' />
								<p>{data.time_stamp}</p>
							</CardContent>
						</Card>
					))}
			</main>
			<div className='fixed bottom-2 left-2 rounded-full text-center'>
				<Button className='w-16 h-16 rounded-full'>
					<Link to='/addperson' className='flex items-center justify-center'>
						<UserPlus size={30} style={{ width: "30px", height: "30px" }} />
					</Link>
				</Button>
			</div>
			<div className='fixed bottom-2 right-2 rounded-full text-center ring-offset-blue'>
				<Button className='w-16 h-16 rounded-full'>
					<Link to='/add' className='flex items-center justify-center'>
						<Plus size={30} style={{ width: "30px", height: "30px" }} />
					</Link>
				</Button>
			</div>
		</div>
	);
};

export default Home;
