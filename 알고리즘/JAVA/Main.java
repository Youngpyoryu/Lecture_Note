import java.io.BufferedReader;
//입력 스트림 처리 : 빠르게 입력을 받을 수 있는 BufferedReader 클래스를 사용하기 위해
import java.io.IOException;
//입출력 도중 발생할 수 있는 입출력 예외(IOException)를 처리하기 위해
import java.io.InputStreamReader;
//BufferedReader와 표준 입력을 연결하기 위한 InputReader클래스를 사용하기 위해
import java.util.Arrays;
//배열을 쉽게 정렬할 수 있는 Arrays 유틸리티 클래스 사용을 하기 위해
import java.util.Comparator;
//comparator 인터페이스를 사용하여 2차원 배열의 정렬 기준을 정의하기 위해
import java.util.StringTokenizer;
// 입력받은 문자열을 공백을 기준으로 나누기 위해 

public class Main {
	public static void main(String[] args) throws IOException { //throws IOException을 통해 입출력 관련 예외 발생시 처리
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in)); // 표준입력(System.in)을 BufferedReader를 통해 읽을 수 있도록 연결
		StringBuffer sb = new StringBuffer(); //결과를 빠르게 출력하기 위해 StringBuler객체를 생성. 이 객체에 정렬된 결과를 저장하고 한꺼번에 출력할 에정
		int N = Integer.parseInt(br.readLine()); // 첫 번째 줄에 입력된 숫자를 받아서 N에 저장

		StringTokenizer st;
		int[][] arr = new int[N][2]; //2차원 배열 선언 : 좌표를 저장하 기 위해 크기 NX2의 차원 배열 arr을 선언
		// 입력
		for (int i = 0; i < arr.length; i++) {
			st = new StringTokenizer(br.readLine(), " "); // 좌표입력처리 : StringTokenizer를 사용하여 좌표의 두값을 분리.
			arr[i][0] = Integer.parseInt(st.nextToken()); //x좌표 저장
			arr[i][1] = Integer.parseInt(st.nextToken()); //y좌표 저장

		}

		// x좌표가 증가하는 순으로, x좌표가 같으면 y좌표가 증가하는 순서로 정렬
		Arrays.sort(arr, new Comparator<int[]>() { // 배열 정리 시작 

			@Override //comparator 오버라이드
			public int compare(int[] o1, int[] o2) {
				if (o1[0] == o2[0]) //y좌표 비교 : 만약 두 좌표의 x값이 같다면, y값을 비교함. y값이 작은 순으로 정렬
					return o1[1] - o2[1];
				else
					return o1[0] - o2[0]; // x좌표 비 : 두 좌표의 x값이 다르면, x값을 기준으로 오름차순으로 정렬
			}
		});
		
		// 출력
		for (int i = 0; i < arr.length; i++) {
			sb.append(arr[i][0] + " " + arr[i][1]).append("\\n");
		}
		System.out.println(sb);
	}

}