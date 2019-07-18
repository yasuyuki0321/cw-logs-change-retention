# 概要
cloudwatch logsの保存期間を一律変更する

# 前提条件
Serverless Frameworkがインストールされてること  
https://serverless.com/
https://serverless.com/framework/docs/providers/aws/guide/installation/

# 使い方
## リポジトリをクローン
```
git clone https://ghe.iret.intra/cloudpack/cloudwatch-logs-change_retention.git
```

## 環境変数
AWSアカウントのアクセスキー/シークレットキーを環境変数に設定する
```
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_ACCESS_KEY_ID=yyy
export AWS_DEFAULT_REGION=ap-northeast-1
```

## デプロイ
```
sls deploy -v 
```

## 実行
Cloudwatch Eventsで日時で0:00に実行するように設定しているが、手動実行する場合には下記のコマンドを実行する
```
sls invoke -f change_retention -l
```
実行時間を変更する場合には、serverless.ymlのeventsの設定を変更

## その他
保存期間はLambdaの環境変数(RETENTION)で変更可能