import { Input } from "@/components/ui/input";
import React, { useEffect } from "react";
import { Button } from "./ui/button";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
	doc,
	getDoc,
	getDocs,
	collection,
	updateDoc,
	addDoc,
} from "firebase/firestore";
import { db } from "@/lib/firebase"; // dbのインポートを追加
import { auth } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import { Card, CardHeader, CardTitle } from "./ui/card";

const AddPerson = () => {
	const [addWord, setAddWord] = useState("");
	const [exchangers, setExchangers] = useState([]);
	const [user] = useAuthState(auth);
	const navigate = useNavigate();
	const getAllNames = async () => {
		const querySnapshot = await getDocs(
			collection(db, "Users", user.uid, "Exchangers")
		);
		const exchanges = querySnapshot.docs.map((doc) => {
			return doc.data();
		});
		setExchangers(exchanges);
		console.log(exchanges);
	};
	const addName = async (e) => {
		e.preventDefault();
		if (addWord === "") return;
		await addDoc(collection(db, "Users", user.uid, "Exchangers"), {
			name: addWord,
		});
		setAddWord("");
		getAllNames();
	};
	useEffect(() => {
		getAllNames();
	}, []);
	return (
		<div>
			<div className='justify-between flex'>
				<Input
					className=' ml-2 my-2'
					placeholder='追加する交換相手の名前を入力'
					onChange={(e) => setAddWord(e.target.value)}
					value={addWord}
				/>
				<Button className='mx-2 my-2' onClick={addName}>
					追加
				</Button>
			</div>
			<div>
				{exchangers.map((exchanger, index) => (
					<Card key={index} className='mx-2 my-2'>
						<CardHeader>
							<CardTitle>{exchanger.name}</CardTitle>
						</CardHeader>
					</Card>
				))}
			</div>
			<div className='w-screen p-2'>
				<Button className='w-full'>
					<Link to='/'>ホームに戻る</Link>
				</Button>
			</div>
		</div>
	);
};

export default AddPerson;
