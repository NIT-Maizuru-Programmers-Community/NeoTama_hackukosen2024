import { Input } from "@/components/ui/input";
import React, { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Link, useNavigate } from "react-router-dom";
import {
	doc,
	getDoc,
	updateDoc,
	getDocs,
	collection,
	setDoc,
	addDoc,
} from "firebase/firestore";
import { db } from "@/lib/firebase"; // dbのインポートを追加
import { auth } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

const Add = () => {
	const [match, setMatch] = useState(false);
	const [searchWord, setSearchWord] = useState("");
	const [imageURL, setImageURL] = useState("");
	const [exchangers, setExchangers] = useState([]);
	const [exchangername, setExchangername] = useState("");
	const [user] = useAuthState(auth);
	const navigate = useNavigate();
	const handleSearch = async () => {
		try {
			// ドキュメント参照を作成
			const docRef = doc(db, "Hard", searchWord); // "Hard"コレクション内の特定のドキュメントIDを指定
			const docSnap = await getDoc(docRef);

			if (docSnap.exists()) {
				const data = docSnap.data();
				if (data.name !== "" && data.display_name !== "" && data.id !== "") {
					alert("認証済みのコードです");
					setSearchWord("");
					return;
				}
				setMatch(true);
				setImageURL(data.url); // ドキュメント内のurlフィールドを取得
			} else {
				alert("指定されたコードのデータが見つかりません");
				setMatch(false);
			}
		} catch (error) {
			setMatch(false);
			console.error("データ取得エラー:", error);
			alert("データの取得に失敗しました");
		}
	};
	const handleUpload = async () => {
		try {
			// ドキュメント参照を作成
			if (exchangername === "") {
				alert("渡す相手を選択してください");
				return;
			}
			const docRef = doc(db, "Hard", searchWord); // "Hard"コレクション内の特定のドキュメントIDを指定
			await updateDoc(docRef, {
				display_name: user.displayName,
				id: user.uid,
				name: exchangername,
			});
			const docSnap = await getDoc(docRef);
			const data = docSnap.data();
			submitAdd(data);
			alert("認証に成功しました");
			setSearchWord("");
			navigate("/");
		} catch (error) {
			console.error("データ更新エラー:", error);
			alert("データの更新に失敗しました");
		}
	};
	const submitAdd = async (data) => {
		await addDoc(collection(db, "Users", user.uid, "Collections"), {
			display_name: data.display_name,
			id: data.id,
			name: data.name,
			time_stamp: data.time_stamp,
			url: data.url,
		});
	};
	const getAllNames = async () => {
		const querySnapshot = await getDocs(
			collection(db, "Users", user.uid, "Exchangers")
		);
		const exchanges = querySnapshot.docs.map((doc) => {
			const docData = doc.data();
			docData.time_stamp = docData.time_stamp.toDate();
			return docData;
		});
		exchanges.sort((a, b) => b.time_stamp - a.time_stamp);
		setExchangers(exchanges);
		console.log(exchanges);
	};
	useEffect(() => {
		getAllNames();
	}, []);

	return (
		<div>
			<div className='justify-between flex'>
				<Input
					className=' ml-2 my-2'
					placeholder='認証コードを入力'
					value={searchWord}
					onChange={(e) => setSearchWord(e.target.value)}
				/>
				<Button className='mx-2 my-2' onClick={handleSearch}>
					検索
				</Button>
			</div>
			<div className='w-screen px-2 pb-2'>
				<Select onValueChange={(value) => setExchangername(value)}>
					<SelectTrigger className='w-full'>
						<SelectValue placeholder='渡す相手を選択' />
					</SelectTrigger>
					<SelectContent>
						{exchangers.map((exchanger, index) => (
							<SelectItem key={index} value={exchanger.name}>
								{exchanger.name}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>
			<div className='px-2'>
				{match && <img src={imageURL} alt='検索結果' className='w-full' />}
			</div>
			<div className='w-screen p-2'>
				{match && (
					<Button className='w-full mb-2' onClick={handleUpload}>
						認証する
					</Button>
				)}
				<Button className='w-full'>
					<Link to='/'>ホームに戻る</Link>
				</Button>
			</div>
		</div>
	);
};

export default Add;
