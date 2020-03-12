/*
insert Entity Suggest
*/
if not exists( select * from Entity where cname = N'國家教育研究院詞彙' and ename = 'naerv' )
	insert into Entity(CName, EName) values(N'國家教育研究院詞彙','naerv')
/*
update CDes nvarchar(4000) -> nvarchar(max)
*/
alter table object alter column CDes nvarchar(max)
go

if exists( select * from sys.objects where object_id=object_id(N'dbo.fn_getBitValue') and type in ('FT', 'FN', 'FS', 'TF', 'IF') )
	drop function dbo.fn_getBitValue
go
/*
Example:
	declare @Value varbinary(64) = 0x0003
	declare @Position int = 9
	select dbo.fn_getBitValue( @Value, @Position )
Description :
	dbo.fn_getBitValue，確認 BinaryData 在 Position 是否為 1 或 0
*/
create function dbo.fn_getBitValue( @Value varbinary(64), @Position int )
	returns bit
begin
	select @value = iif( isnumeric(@Value) = 1, cast( @value as varbinary(max) ), @value )
	declare @Representation varchar(max) = convert( varchar(max), @Value, 2 )
	select @Representation = replace( @Representation, HexDigit, BinaryDigits )
	from (
		  values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111')
	) as f(HexDigit,BinaryDigits)

	return iif( substring( reverse( @Representation ), @Position, 1 ) = '1', 1, 0)
	--case substring( reverse( @Representation ), @Position, 1 ) when '1' then 1 else 0 end
end
go

if exists( select * from sys.objects where object_id=object_id(N'dbo.fn_updateBitValue') and type in ('FT', 'FN', 'FS', 'TF', 'IF') )
	drop function dbo.fn_updateBitValue
go
/*
Example:
	declare @Value varbinary(64) = 0x0003
	declare @Position int = 9
	declare @BitValue bit = 1
	select dbo.fn_updateBitValue( @Value, @Position, @BitValue )
Description :
	dbo.fn_updateBitValue，取得 BinaryData 修改後的值
*/
create function dbo.fn_updateBitValue( @Value varbinary(64), @Position int, @BitValue bit )
	returns varbinary(max)
begin
	select @value = iif( isnumeric(@Value) = 1, cast( @value as varbinary(max) ), @value )
	declare @Representation varchar(max) = convert( varchar(max), @Value, 2 )

	select @Representation = replace( @Representation, HexDigit, BinaryDigits )
	from (
		  values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111')
	) as f(HexDigit,BinaryDigits)

	select @Representation=iif( len(@Representation)< @Position,
				stuff( reverse( replicate( '0', ((@Position/8)+1)*8-len(@Representation))+@Representation ), @Position, 1 , iif( @BitValue = 1, '1', '0' ) ) ,
				stuff( reverse( @Representation ), @Position, 1 , iif( @BitValue = 1, '1', '0' ) ))
	select @Representation=reverse(@Representation)

	;with ConvertHex as
	(
		select replace( left( @Representation, 4 ), BinaryDigits, HexDigit ) as newHex, left( @Representation, 4 ) as LeftBinary, right( @Representation, len(@Representation)-4 ) as RightBinary
		from ( values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111') ) as f(HexDigit,BinaryDigits)
		where @Representation is not null and len( @Representation)-4 > 0 and BinaryDigits = left( @Representation, 4 )
		union all
		select newHex+replace( left( RightBinary, 4 ), BinaryDigits, HexDigit ), left( RightBinary, 4 ) as LeftBinary,  right( RightBinary, len(RightBinary)-4 )
		from ConvertHex, ( values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111') ) as f(HexDigit,BinaryDigits)
		where LeftBinary is not null and len( RightBinary)-4 > 0 and BinaryDigits = left(  RightBinary, 4 )
		union all
		select newHex+replace( left( RightBinary, 4 ), BinaryDigits, HexDigit ), left( RightBinary, 4 ) as LeftBinary,  right( RightBinary, len(RightBinary)-4 )
		from ConvertHex, ( values('0','0000'),('1','0001'),('2','0010'),('3','0011'),('4','0100'),('5','0101'),('6','0110'),('7','0111'),
		  ('8','1000'), ('9','1001'),('A','1010'),('B','1011'),('C','1100'),('D','1101'),('E','1110'),('F','1111') ) as f(HexDigit,BinaryDigits)
		where LeftBinary is not null and len( RightBinary)-4 = 0 and BinaryDigits = left(  RightBinary, 4 )
	 )
	 select top 1 @Representation='0x'+newHex from ConvertHex where RightBinary = ''

	return convert( varbinary(max), @Representation, 1)
end
go

if object_id('dbo.fn_getObjectData') is not null
	drop function dbo.fn_getObjectData
go
/*
Example:
	declare @type int = 1
	declare @divisor int = 5
	declare @remainder int = 1
	select * from dbo.fn_getObjectData(@type, @divisor, @remainder)
Description :
	dbo.fn_getObjectData，取得 Object top 1 Data
*/
create function dbo.fn_getObjectData(
	@eid int,
	@divisor int,
	@remainder int
)
returns table as return(
	-- Databyte (Process bit: N/A | Sentence TP | Text Processor | DOM Parser | Crawler | N/A | N/A | N/A)
    select top 1 o.OID, o.CName, o.CDes, o.Databyte
    from Object o
    where Type = @eid and o.OID % @divisor = @remainder and dbo.fn_getBitValue(isnull(DataByte,0),5)=0
)
go

if object_id('dbo.xp_insertObjectData') is not null
	drop procedure dbo.xp_insertObjectData
go
/*
Example:
	--['46', '1007429', '化學名詞-有機化合物', 'sulfathiazole sodium', '磺胺噻唑鈉']
	declare @idx int = 46
	declare @val int = 1007429
	declare @category nvarchar(max) = N'化學名詞-有機化合物'
	declare @ename nvarchar(max) = 'sulfathiazole sodium'
	declare @cname nvarchar(max) = N'磺胺噻唑鈉'
	exec dbo.xp_insertObjectData @idx, @val, @category, @ename, @cname
Description :
	dbo.xp_insertObjectData，插入一筆資料
*/
create procedure dbo.xp_insertObjectData(
	@idx int,
	@val int,
	@category nvarchar(max),
	@ename nvarchar(max),
	@cname nvarchar(max)
)
as 
begin
	begin try
		set nocount on
		declare @EID int, @OID int, @CID int, @newCID int, @nlevel int

		if not exists( select * from Entity where cname = N'國家教育研究院詞彙' and ename = 'naerv' )
			insert into Entity(CName, EName) values(N'國家教育研究院詞彙','naerv')
		else
			select @EID = EID from Entity where cname = N'國家教育研究院詞彙' and ename = 'naerv'
		
		-- (1.) not exists -> insert or exists -> update
		if not exists( select * from Object where CName = @cname and EName = @ename and cdes = @category )
		begin
			insert into Object(Type, CName, EName, CDes, nInlinks, nOutlinks) values (@EID, @cname, @ename, @category, @idx, @val)	
			select @OID = scope_identity()
		end
		else
			select @OID = OID from Object where CName = @cname and EName = @ename and cdes = @category 

		select @CID = CID from Class where Type = @EID and CName = N''+@category
		if @CID is null and @OID is not null
		begin
			select @CID = CID from Class where Type = @EID and CName = N'國家教育研究院詞彙'
			exec dbo.xps_insertClass @CID, @EID, @category, null, null, @newCID output
			insert into CO(CID, OID) values(@newCID, @OID)
		end
		else if not exists( select * from CO where CID = @CID and OID = @OID )
		begin
			insert into CO(CID, OID) values(@CID, @OID)
		end
		set nocount off
	end try
	begin catch
	--系統拋回訊息用
		DECLARE @ErrorMessage As VARCHAR(1000) = CHAR(10)+'錯誤代碼：' +CAST(ERROR_NUMBER() AS VARCHAR)
												+CHAR(10)+'錯誤訊息：'+	ERROR_MESSAGE()
												+CHAR(10)+'錯誤行號：'+	CAST(ERROR_LINE() AS VARCHAR)
												+CHAR(10)+'錯誤程序名稱：'+	ISNULL(ERROR_PROCEDURE(),'')
		DECLARE @ErrorSeverity As Numeric = ERROR_SEVERITY()
		DECLARE @ErrorState As Numeric = ERROR_STATE()
		RAISERROR( @ErrorMessage, @ErrorSeverity, @ErrorState);--回傳錯誤資訊
	end catch
	return
end
go