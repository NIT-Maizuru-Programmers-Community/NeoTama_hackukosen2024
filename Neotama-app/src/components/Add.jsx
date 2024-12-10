import { Input } from "@/components/ui/input";
import React from "react";
import { Button } from "./ui/button";
import { useState } from "react";
import { Link } from "react-router-dom";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { db } from "@/lib/firebase"; // dbのインポートを追加
import { auth } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";

const Add = () => {
	const [match, setMatch] = useState(false);
	const [searchWord, setSearchWord] = useState("");
	const [imageURL, setImageURL] = useState("");
	const [user] = useAuthState(auth);
	const handleSearch = async () => {
		try {
			// ドキュメント参照を作成
			const docRef = doc(db, "Hard", searchWord); // "Hard"コレクション内の特定のドキュメントIDを指定
			const docSnap = await getDoc(docRef);

			if (docSnap.exists()) {
				const data = docSnap.data();
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
	const handleUpdate = async () => {
		try {
			// ドキュメント参照を作成
			const docRef = doc(db, "Hard", searchWord); // "Hard"コレクション内の特定のドキュメントIDを指定
			await updateDoc(docRef, {
				display_name: user.displayName,
				id: user.uid,
			});
		} catch (error) {
			console.error("データ更新エラー:", error);
			alert("データの更新に失敗しました");
		}
	};
	return (
		<div>
			<div className='justify-between flex'>
				<Input
					className=' ml-2 my-2'
					onChange={(e) => setSearchWord(e.target.value)}
				/>
				<Button className='mx-2 my-2' onClick={handleSearch}>
					検索
				</Button>
			</div>
			{match && <img src={imageURL} alt='検索結果' className='w-full' />}
			<div className='w-screen p-5'>
				{match ? (
					<Button className='w-full' onClick={handleUpdate}>
						認証する
					</Button>
				) : (
					<Button className='w-full'>
						<Link to='/'>ホームに戻る</Link>
					</Button>
				)}
			</div>
		</div>
	);
};

export default Add;
